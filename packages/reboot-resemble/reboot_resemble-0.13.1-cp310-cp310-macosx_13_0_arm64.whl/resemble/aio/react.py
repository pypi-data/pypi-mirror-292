import asyncio
import grpc
import grpc_status._async as rpc_status_async
import logging
import resemble.aio.placement
import traceback
import uuid
import websockets
from google.protobuf.json_format import MessageToJson
from google.rpc import code_pb2, status_pb2
from grpc_status import rpc_status
from resemble.aio.aborted import Aborted, SystemAborted
from resemble.aio.headers import (
    APPLICATION_ID_HEADER,
    SERVICE_NAME_HEADER,
    STATE_REF_HEADER,
    Headers,
)
from resemble.aio.internals.contextvars import use_application_id
from resemble.aio.internals.middleware import Middleware
from resemble.aio.types import ApplicationId, ServiceName, StateRef
from resemble.settings import EVERY_LOCAL_NETWORK_ADDRESS
from resemble.v1alpha1 import react_pb2, react_pb2_grpc
from resemble.v1alpha1.errors_pb2 import UnknownService
from respect.logging import get_logger
from typing import AsyncIterable, Optional

logger = get_logger(__name__)

# We set the log level to `ERROR` here because websockets is chatty!
logger.setLevel(logging.ERROR)


class ReactServicer(react_pb2_grpc.ReactServicer):
    """System service for serving requests from our code generated react
    readers.

    TODO(benh): make this more generic than just for react so that
    users and other system services (e.g., a read cache) can use this
    to get reactive/streaming reads without the user having to
    implement it themselves.
    """

    def __init__(
        self,
        application_id: ApplicationId,
        middleware_by_service_name: dict[ServiceName, Middleware],
    ):
        self._application_id = application_id
        self._middleware_by_service_name = middleware_by_service_name

        self._stop_websockets_serve = asyncio.Event()

    async def start(self, websocket_port: Optional[int]) -> int:
        """Starts the websocket server and returns the port that it is
        listening on."""
        websocket_bound_port: asyncio.Future[int] = asyncio.Future()

        async def websockets_serve():
            async with websockets.serve(
                self.serve,
                EVERY_LOCAL_NETWORK_ADDRESS,
                websocket_port,
                logger=logger,
            ) as server:
                # server.sockets is of type Iterable[socket] but is not
                # guaranteed to be an indexable list.
                socket = next(iter(server.sockets))
                websocket_bound_port.set_result(socket.getsockname()[1])
                await self._stop_websockets_serve.wait()

        self._websockets_serve_task = asyncio.create_task(
            websockets_serve(),
            name=f'websockets_serve() in {__name__}',
        )

        await websocket_bound_port

        return websocket_bound_port.result()

    async def stop(self):
        self._stop_websockets_serve.set()
        try:
            await self._websockets_serve_task
        except:
            # We're trying to stop so no need to propagate any
            # exceptions.
            pass

    async def serve(self, websocket):
        with use_application_id(self._application_id):
            try:
                application_id, service_name, state_ref = (
                    websocket.request_headers[APPLICATION_ID_HEADER],
                    websocket.request_headers[SERVICE_NAME_HEADER],
                    StateRef(websocket.request_headers[STATE_REF_HEADER]),
                )

                assert self._application_id == application_id

                middleware: Optional[Middleware] = (
                    self._middleware_by_service_name.get(service_name)
                )

                if middleware is None:
                    logger.error(
                        "Attempted to perform a 'React' mutation to an unknown "
                        f"service '{service_name}'; "
                        "did you bring up a servicer for it in your `Application`?"
                    )
                    return

                async for request_bytes in websocket:
                    try:
                        request = react_pb2.MutateRequest()
                        request.ParseFromString(request_bytes)

                        headers = Headers(
                            application_id=application_id,
                            service_name=service_name,
                            state_ref=state_ref,
                            idempotency_key=uuid.UUID(request.idempotency_key),
                            bearer_token=request.bearer_token,
                        )

                        response = await middleware.react_mutate(
                            headers,
                            request.method,
                            request.request,
                        )

                        await websocket.send(
                            react_pb2.MutateResponse(
                                response=response.SerializeToString(),
                            ).SerializeToString()
                        )
                    except asyncio.CancelledError:
                        # It's pretty normal for a query to be
                        # cancelled; it's not useful to print a stack
                        # trace.
                        raise
                    except Aborted as aborted:
                        await websocket.send(
                            react_pb2.MutateResponse(
                                status=MessageToJson(aborted.to_status()),
                            ).SerializeToString()
                        )
                    except websockets.exceptions.ConnectionClosedOK:
                        # No real error here, browser users will come and go!
                        raise
                    except websockets.exceptions.ConnectionClosedError:
                        # No real error here, browser users may get disconnected!
                        raise
                    except BaseException as exception:
                        # Print the exception stack trace for easier
                        # debugging. Note that we don't include the stack
                        # trace in an error message for the same reason
                        # that gRPC doesn't do so by default, see
                        # https://github.com/grpc/grpc/issues/14897, but
                        # since this should only get logged on the server
                        # side it is safe.
                        logger.error(
                            'Failed to execute mutation via websocket; '
                            f'{type(exception).__name__}: {exception}'
                        )

                        # TODO: send a status which does not include any
                        # details, just a message which we glean from the
                        # raised exception.
                        status = status_pb2.Status(
                            code=code_pb2.Code.UNKNOWN,
                            message=f'{type(exception).__name__}: {exception}',
                        )
                        await websocket.send(
                            react_pb2.MutateResponse(
                                status=MessageToJson(status),
                            ).SerializeToString()
                        )
            except websockets.exceptions.ConnectionClosedOK:
                # No real error here, browser users will come and go!
                pass
            except websockets.exceptions.ConnectionClosedError:
                # No real error here, browser users may get disconnected!
                pass

    def add_to_server(self, server: grpc.aio.Server) -> None:
        react_pb2_grpc.add_ReactServicer_to_server(self, server)

    async def Query(
        self,
        request: react_pb2.QueryRequest,
        grpc_context: grpc.aio.ServicerContext,
    ) -> AsyncIterable[react_pb2.QueryResponse]:
        """Implements the React.Query RPC that calls into the
        'Middleware.react' method for handling the request."""
        # NOTE: we don't need `with use_application_id(...)` like we
        # do for websockets because this is a gRPC method and thus our
        # `UseApplicationIdInterceptor` will have already done it for
        # us.
        try:
            headers = Headers.from_grpc_context(grpc_context)
            assert headers.application_id is not None  # Guaranteed by `Headers`.

            middleware: Optional[Middleware] = (
                self._middleware_by_service_name.get(headers.service_name)
            )

            if middleware is None:
                logger.error(
                    "Attempted to perform a 'React' query to an unknown "
                    f"service '{headers.service_name}'; "
                    "did you bring up a servicer for it in your `Application`?"
                )
                raise SystemAborted(UnknownService())

            # Determine whether this is the right consensus to serve this
            # request.
            try:
                authoritative_consensus = middleware.placement_client.consensus_for_actor(
                    headers.application_id, headers.service_name,
                    headers.state_ref
                )
            except resemble.aio.placement.UnknownApplicationError:
                # It's possible that the user did indeed type an application ID
                # that doesn't exist, but it's also quite possible that this
                # request reached us before the placement planner had gossipped
                # out the information about which applications exist (we see
                # this e.g. after `rsm dev`'s chaos monkey restarts). For that
                # reason, abort with a retryable error.
                await grpc_context.abort(
                    grpc.StatusCode.UNAVAILABLE,
                    f"Application '{headers.application_id}' not found. If you "
                    "are confident the application exists, this may be because "
                    "the system is still starting."
                )
                raise RuntimeError("This code is unreachable")

            if authoritative_consensus != middleware.consensus_id:
                # This is NOT the correct consensus. Forward to the correct one.
                correct_address = middleware.placement_client.address_for_consensus(
                    authoritative_consensus
                )
                channel = middleware.channel_manager.get_channel_to(
                    correct_address
                )
                stub = react_pb2_grpc.ReactStub(channel)
                call = stub.Query(
                    metadata=grpc_context.invocation_metadata(),
                    request=request
                )
                try:
                    async for response in call:
                        yield response
                except grpc.aio.AioRpcError as error:
                    # Reconstitute the error that the server threw.
                    status = await rpc_status_async.from_call(call)
                    if status is not None:
                        raise SystemAborted.from_status(status) from None
                    raise SystemAborted.from_grpc_aio_rpc_error(
                        error
                    ) from None

            async for (response, idempotency_keys) in middleware.react_query(
                grpc_context,
                headers,
                request.method,
                request.request,
            ):
                yield react_pb2.QueryResponse(
                    response=(
                        response.SerializeToString()
                        if response is not None else None
                    ),
                    idempotency_keys=[
                        str(idempotency_key)
                        for idempotency_key in idempotency_keys
                    ],
                )
        except asyncio.CancelledError:
            # It's pretty normal for a query to be cancelled; it's not useful to
            # print a stack trace.
            raise
        except grpc.aio.BaseError:
            # If somewhere deeper in the call graph had a gRPC error
            # just let that propagate!
            raise
        except Aborted as aborted:
            await grpc_context.abort_with_status(
                rpc_status.to_status(aborted.to_status())
            )
        except BaseException as exception:
            # Don't print a stack trace for any common errors or user
            # errors that were raised that we turned into an
            # `Aborted`. We should have logged an error to make it
            # easier for a user to debug.
            #
            # As of the writing of this comment we know that if the
            # context status code is `ABORTED` then it must have been
            # from our `Aborted` because there aren't any other ways
            # for Resemble apps to abort an RPC because we don't give
            # them access to a `ServicerContext`. But even if we do,
            # if a user calls abort then that's similar to raising one
            # of their user errors and we probably don't need to print
            # a stack trace.
            if (
                grpc_context.code() != code_pb2.Code.ABORTED and
                not isinstance(exception, GeneratorExit)
            ):
                traceback.print_exc()

            raise exception

    async def WebSocketsConnection(
        self,
        request: react_pb2.WebSocketsConnectionRequest,
        grpc_context: grpc.aio.ServicerContext,
    ) -> react_pb2.WebSocketsConnectionResponse:
        await asyncio.Event().wait()
        # TODO(benh): use `assert_never` in Python > 3.11.
        assert False, 'Unreachable'
