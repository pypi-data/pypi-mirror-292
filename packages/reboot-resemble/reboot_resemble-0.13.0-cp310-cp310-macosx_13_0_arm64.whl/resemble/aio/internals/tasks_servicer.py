import asyncio
import grpc
from resemble.aio.auth.admin_auth import AdminAuthMixin
from resemble.aio.internals.channel_manager import _ChannelManager
from resemble.aio.internals.middleware import Middleware
from resemble.aio.internals.tasks_cache import TasksCache
from resemble.aio.placement import PlacementClient
from resemble.aio.state_managers import StateManager
from resemble.aio.types import (
    ApplicationId,
    ConsensusId,
    ServiceName,
    StateRef,
    StateTypeName,
    state_type_to_service,
)
from resemble.consensus.sidecar import NonexistentTaskId
from resemble.v1alpha1 import tasks_pb2, tasks_pb2_grpc
from typing import Optional


class TasksServicer(
    AdminAuthMixin,
    tasks_pb2_grpc.TasksServicer,
):

    def __init__(
        self,
        state_manager: StateManager,
        cache: TasksCache,
        placement_client: PlacementClient,
        channel_manager: _ChannelManager,
        application_id: ApplicationId,
        consensus_id: ConsensusId,
        middleware_by_service_name: dict[ServiceName, Middleware],
    ):
        super().__init__()

        self._cache = cache
        self._state_manager = state_manager
        self._placement_client = placement_client
        self._channel_manager = channel_manager
        self._application_id = application_id
        self._consensus_id = consensus_id
        self._middleware_by_service_name = middleware_by_service_name

    def add_to_server(self, server: grpc.aio.Server) -> None:
        tasks_pb2_grpc.add_TasksServicer_to_server(self, server)

    async def Wait(
        self,
        request: tasks_pb2.WaitRequest,
        grpc_context: grpc.aio.ServicerContext,
    ) -> tasks_pb2.WaitResponse:
        """Implementation of Tasks.Wait()."""
        # Determine whether this is the right consensus to serve this request.
        authoritative_consensus = self._placement_client.consensus_for_actor(
            self._application_id,
            state_type_to_service(StateTypeName(request.task_id.state_type)),
            StateRef(request.task_id.state_ref),
        )
        if authoritative_consensus != self._consensus_id:
            # This is NOT the correct consensus. Forward to the correct one.
            correct_address = self._placement_client.address_for_consensus(
                authoritative_consensus
            )
            channel = self._channel_manager.get_channel_to(correct_address)
            stub = tasks_pb2_grpc.TasksStub(channel)
            return await stub.Wait(
                metadata=grpc_context.invocation_metadata(),
                request=request,
            )

        cached_response = await self._cache.get(request.task_id)

        if cached_response is not None:
            response_or_error = tasks_pb2.TaskResponseOrError()
            response_or_error.ParseFromString(cached_response)
            return tasks_pb2.WaitResponse(response_or_error=response_or_error)

        # Task is not cached; try and load it via the state manager.
        try:
            sidecar_response_or_error: Optional[
                tasks_pb2.TaskResponseOrError] = (
                    await
                    self._state_manager.load_task_response(request.task_id)
                )
        except NonexistentTaskId:
            await grpc_context.abort(code=grpc.StatusCode.NOT_FOUND)
        else:
            # Invariant: 'response' must not be 'None'.
            #
            # Explanation: For an unknown task_id,
            # load_task_response() will raise, so to get here, task_id
            # must belong to a valid, but evicted, task. We only evict
            # tasks from our cache if they have completed, and
            # completed tasks are required to have a response stored
            # (although that response may itself be empty).
            assert sidecar_response_or_error is not None

            # Cache the task response for temporal locality.
            self._cache.put_with_response(
                request.task_id, sidecar_response_or_error.SerializeToString()
            )

            return tasks_pb2.WaitResponse(
                response_or_error=sidecar_response_or_error
            )

    async def _aggregate_all_pending_tasks(
        self,
        grpc_context: grpc.aio.ServicerContext,
    ) -> tasks_pb2.ListPendingTasksResponse:

        async def call_other_consensus(
            consensus_id: ConsensusId,
            list_pending_tasks_responses: list[
                tasks_pb2.ListPendingTasksResponse],
        ):
            """
            Calls 'ListPendingTasks' on the given consensus and appends the
            response to 'list_pending_tasks_responses'.
            """
            channel = self._channel_manager.get_channel_to(
                self._placement_client.address_for_consensus(consensus_id)
            )
            stub = tasks_pb2_grpc.TasksStub(channel)
            response = await stub.ListPendingTasks(
                tasks_pb2.ListPendingTasksRequest(
                    only_consensus_id=consensus_id
                ),
                metadata=grpc_context.invocation_metadata(),
            )
            list_pending_tasks_responses.append(response)

        list_pending_tasks_responses: list[tasks_pb2.ListPendingTasksResponse
                                          ] = []

        consensus_ids = self._placement_client.known_consensuses(
            self._application_id
        )

        await asyncio.gather(
            *(
                call_other_consensus(
                    consensus_id,
                    list_pending_tasks_responses,
                ) for consensus_id in consensus_ids
            )
        )

        result = tasks_pb2.ListPendingTasksResponse()
        for response in list_pending_tasks_responses:
            result.task_ids.extend(response.task_ids)

        return result

    async def ListPendingTasks(
        self,
        request: tasks_pb2.ListPendingTasksRequest,
        grpc_context: grpc.aio.ServicerContext,
    ) -> tasks_pb2.ListPendingTasksResponse:
        """Implementation of Tasks.ListPendingTasks()."""
        await self.ensure_admin_auth_or_fail(grpc_context)

        if not request.HasField("only_consensus_id"):
            # Give all pending tasks across all consensuses.
            return await self._aggregate_all_pending_tasks(grpc_context)
        elif request.only_consensus_id == self._consensus_id:
            return tasks_pb2.ListPendingTasksResponse(
                task_ids=self._cache.get_pending_tasks()
            )

        # This is NOT the correct consensus. Forward to the correct one.
        correct_address = self._placement_client.address_for_consensus(
            request.only_consensus_id
        )
        channel = self._channel_manager.get_channel_to(correct_address)
        stub = tasks_pb2_grpc.TasksStub(channel)
        return await stub.ListPendingTasks(
            metadata=grpc_context.invocation_metadata(),
            request=request,
        )

    async def CancelTask(
        self,
        request: tasks_pb2.CancelTaskRequest,
        grpc_context: grpc.aio.ServicerContext,
    ) -> tasks_pb2.CancelTaskResponse:
        """Implementation of Tasks.CancelTask()."""
        await self.ensure_admin_auth_or_fail(grpc_context)

        # Determine whether this is the right consensus to serve this request.
        authoritative_consensus = self._placement_client.consensus_for_actor(
            self._application_id,
            state_type_to_service(StateTypeName(request.task_id.state_type)),
            StateRef(request.task_id.state_ref),
        )
        if authoritative_consensus != self._consensus_id:
            # This is NOT the correct consensus. Forward to the correct one.
            correct_address = self._placement_client.address_for_consensus(
                authoritative_consensus
            )
            channel = self._channel_manager.get_channel_to(correct_address)
            stub = tasks_pb2_grpc.TasksStub(channel)
            return await stub.CancelTask(
                metadata=grpc_context.invocation_metadata(),
                request=request,
            )

        middleware: Optional[
            Middleware] = self._middleware_by_service_name.get(
                state_type_to_service(request.task_id.state_type)
            )

        if middleware is None:
            raise ValueError(
                f"Unknown state type '{request.task_id.state_type}'"
            )

        return await middleware.tasks_dispatcher.cancel_task(
            request.task_id.task_uuid
        )
