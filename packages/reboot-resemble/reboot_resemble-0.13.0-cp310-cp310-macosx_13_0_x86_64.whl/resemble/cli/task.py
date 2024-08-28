import grpc
import json
import uuid
from google.protobuf import json_format
from resemble.aio.external import ExternalContext
from resemble.aio.headers import AUTHORIZATION_HEADER
from resemble.aio.types import StateRef, StateTypeName
from resemble.cli import terminal
from resemble.cli.rc import ArgumentParser, add_common_channel_args
from resemble.v1alpha1 import tasks_pb2, tasks_pb2_grpc
from typing import Optional


def register_task(parser: ArgumentParser):
    """Register the 'task' subcommand with the given parser."""

    def _add_common_args(subcommand):
        add_common_channel_args(subcommand)

        # Should be able to use 'rsm task' with 'rsm dev run' without an admin
        # secret.
        subcommand.add_argument(
            '--admin-bearer-token',
            type=str,
            help=(
                "the admin secret to use for authentication. Not necessary "
                "when running 'rsm dev', but must be set in production."
            ),
        )

    list_command = parser.subcommand('task list')
    _add_common_args(list_command)

    cancel_command = parser.subcommand('task cancel')
    _add_common_args(cancel_command)

    cancel_command.add_argument(
        '--state-type',
        type=str,
        help="the state type of the service which holds the task",
        required=True,
    )

    cancel_command.add_argument(
        '--state-id',
        type=str,
        help="the state ID which holds the task",
        required=True,
    )

    cancel_command.add_argument(
        '--task-uuid',
        type=str,
        help="the UUID of the task to cancel",
        required=True,
    )


def _get_metadata(args) -> Optional[tuple[tuple[str, str]]]:
    """Get the metadata for the gRPC call."""
    if args.admin_bearer_token is None:
        return None

    # This token should match what the user stored in their prod secrets.
    return ((AUTHORIZATION_HEADER, f"Bearer {args.admin_bearer_token}"),)


def _get_tasks_stub(args) -> tasks_pb2_grpc.TasksStub:
    """Get a stub for the tasks service."""
    context = ExternalContext(
        name="resemble-cli",
        gateway=args.gateway_address,
        secure_channel=args.gateway_secure_channel,
    )
    return tasks_pb2_grpc.TasksStub(context.legacy_grpc_channel())


async def task_list(args) -> None:
    """Implementation of the 'tasks list' subcommand."""

    stub = _get_tasks_stub(args)
    metadata = _get_metadata(args)
    try:
        pending_tasks = await stub.ListPendingTasks(
            tasks_pb2.ListPendingTasksRequest(),
            metadata=metadata,
        )
    except grpc.aio.AioRpcError as e:
        terminal.fail(f"Failed to list pending tasks: {e.details()}")

    terminal.info("Pending tasks:")

    task_dicts = [
        {
            **json_format.MessageToDict(
                task_id, preserving_proto_field_name=True
            ), 'task_uuid':
                task_id.task_uuid.hex()
        } for task_id in pending_tasks.task_ids
    ]
    json_output = json.dumps(task_dicts, indent=2)
    terminal.info(json_output)


async def task_cancel(args) -> None:
    """Implementation of the 'tasks cancel' subcommand."""

    stub = _get_tasks_stub(args)
    metadata = _get_metadata(args)
    task_uuid = uuid.UUID(args.task_uuid)
    task_id = tasks_pb2.TaskId(
        state_type=args.state_type,
        state_ref=StateRef.from_id(
            StateTypeName(args.state_type), args.state_id
        ).to_str(),
        task_uuid=task_uuid.bytes,
    )

    try:
        cancel_task_response = await stub.CancelTask(
            tasks_pb2.CancelTaskRequest(task_id=task_id),
            metadata=metadata,
        )

        if cancel_task_response.status == tasks_pb2.CancelTaskResponse.Status.OK:
            terminal.info("Task cancelled.")
        elif cancel_task_response.status == tasks_pb2.CancelTaskResponse.Status.NOT_FOUND:
            terminal.fail("Task is not running.")
        elif cancel_task_response.status == tasks_pb2.CancelTaskResponse.Status.CANCELLING:
            terminal.fail("Task is cancelling.")
    except grpc.aio.AioRpcError as e:
        terminal.fail(f"Failed to cancel task: {e.details()}")
