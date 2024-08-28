import pickle
import uuid
from resemble.aio.auth.app_internal_auth import AppInternalAuth
from resemble.aio.contexts import (
    ReaderContext,
    WorkflowContext,
    WriterContext,
    until,
)
from resemble.aio.types import assert_type
from resemble.memoize.v1.memoize_rsm import (
    Memoize,
    ResetRequest,
    ResetResponse,
    StartRequest,
    StartResponse,
    StatusRequest,
    StatusResponse,
    StoreRequest,
    StoreResponse,
)
from typing import Awaitable, Callable, Optional, TypeVar, overload

T = TypeVar('T')


class AtMostOnceFailedBeforeCompleting(Exception):
    """Raised for any repeat attempts at performing an "at most once"
    operation that was started but didn't complete.
    """
    pass


async def memoize(
    idempotency_alias: str,
    context: WorkflowContext,
    callable: Callable[[], Awaitable[T]],
    *,
    type_t: type[T],
    at_most_once: bool,
    retryable_exceptions: Optional[list[type[Exception]]] = None,
    # TODO: idempotency_lifetime: Optional[...] = None,
) -> T:
    """Memoizes the result of running `callable`, only attempting to do so
    once if `at_most_once=True`.

    NOTE: this is the Python wrapper for `resemble.memoize.v1` and as
    such uses `pickle` to serialize the result of calling `callable`
    which therefore must be pickle-able.
    """
    assert_type(context, [WorkflowContext])

    assert context.task_id is not None

    # First make sure we've constructed the state by calling the
    # writer `Reset`, but idempotently so we only do it the first
    # time.
    #
    # TODO(benh): colocate with `context.state_ref` for performance.
    memoize = Memoize.lookup(
        str(uuid.uuid5(context.task_id, idempotency_alias)),
    )

    await memoize.idempotently(
        f'{idempotency_alias} initial reset',
    ).Reset(context)

    status = await memoize.Status(context)

    if at_most_once and status.started and not status.stored:
        raise AtMostOnceFailedBeforeCompleting()
    elif status.stored:
        t = pickle.loads(status.data)
        if type(t) is not type_t:
            raise TypeError(
                f"Stored result of type '{type(t).__name__}' from 'callable' "
                f"is not of expected type '{type_t.__name__}'; have you changed "
                "the 'type' that you expect after having stored a result?"
            )
        return t

    # Only need to call `Start` for "at most once" semantics.
    if at_most_once:
        assert not status.started
        await memoize.idempotently(
            # Generate a random idempotency key because we want to do
            # this each and every time since we might have "reset" if
            # we caught a retryable exception.
            key=uuid.uuid4(),
        ).Start(context)

    try:
        t = await callable()
    except BaseException as exception:
        if at_most_once and retryable_exceptions is not None and any(
            isinstance(exception, retryable_exception)
            for retryable_exception in retryable_exceptions
        ):
            # Only need to reset for "at most once" semantics.
            #
            # NOTE: it's possible that we won't be able to call
            # `Reset` before we fail and even though this "at most
            # once" could be retried it won't be. But the same is true
            # if we failed before we even called `callable` above!
            # While we're eliminating the possibility of trying to
            # call `callable` more than once, we are not ensuring it
            # is called at least once.
            await memoize.idempotently(
                # Generate a random idempotency key because we
                # want to do this each and every time we get one
                # of these exceptions!
                key=uuid.uuid4(),
            ).Reset(context)
        raise
    else:
        # TODO(benh): retry just this part in the event of retryable
        # errors so that we aren't the cause of raising
        # `AtMostOnceFailedBeforeCompleting`.
        await memoize.idempotently(f'{idempotency_alias} store').Store(
            context,
            data=pickle.dumps(t),
        )

        # NOTE: we validate _after_ we have stored in the event that
        # the user just passed an incorrect `validate` they can simply
        # fix that and everything else will just work. Worst case
        # scenario, they can change the idempotency alias/key so that
        # the callable is re-executed.
        #
        # This is technically not required as we'll check the type
        # when we return an already memoized result, but this helps
        # find bugs sooner.
        if type(t) is not type_t:
            raise TypeError(
                f"Result of type '{type(t).__name__}' from 'callable' is "
                f"not of expected type '{type_t.__name__}'; "
                "did you specify an incorrect 'type'?"
            )

        return t


@overload
async def at_most_once(
    idempotency_alias: str,
    context: WorkflowContext,
    callable: Callable[[], Awaitable[None]],
    *,
    type: type = type(None),
    retryable_exceptions: Optional[list[type[Exception]]] = None,
    # TODO: idempotency_lifetime: Optional[...] = None,
) -> None:
    ...


@overload
async def at_most_once(
    idempotency_alias: str,
    context: WorkflowContext,
    callable: Callable[[], Awaitable[T]],
    *,
    type: type[T],
    retryable_exceptions: Optional[list[type[Exception]]] = None,
    # TODO: idempotency_lifetime: Optional[...] = None,
) -> T:
    ...


async def at_most_once(
    idempotency_alias: str,
    context: WorkflowContext,
    callable: Callable[[], Awaitable[T]],
    *,
    type: type = type(None),
    retryable_exceptions: Optional[list[type[Exception]]] = None,
    # TODO: idempotency_lifetime: Optional[...] = None,
) -> T:
    """Attempts to run and memoize the result of calling `callable` but
    only once.

    NOTE: this is the Python wrapper for `resemble.memoize.v1` and as
    such uses `pickle` to serialize the result of calling `callable`
    which therefore must be pickle-able.
    """
    return await memoize(
        idempotency_alias,
        context,
        callable,
        type_t=type,
        at_most_once=True,
        retryable_exceptions=retryable_exceptions,
    )


@overload
async def at_least_once(
    idempotency_alias: str,
    context: WorkflowContext,
    callable: Callable[[], Awaitable[None]],
    *,
    type: type = type(None),
    # TODO: idempotency_lifetime: Optional[...] = None,
) -> None:
    ...


@overload
async def at_least_once(
    idempotency_alias: str,
    context: WorkflowContext,
    callable: Callable[[], Awaitable[T]],
    *,
    type: type[T],
    # TODO: idempotency_lifetime: Optional[...] = None,
) -> T:
    ...


async def at_least_once(
    idempotency_alias: str,
    context: WorkflowContext,
    callable: Callable[[], Awaitable[T]],
    *,
    type: type = type(None),
    # TODO: idempotency_lifetime: Optional[...] = None,
) -> T:
    """Attempts to run and memoize the result of calling `callable` while
    supporting retrying as many times as necessary until `callable`
    succeeds.

    NOTE: this is the Python wrapper for `resemble.memoize.v1` and as
    such uses `pickle` to serialize the result of calling `callable`
    which therefore must be pickle-able.
    """
    return await memoize(
        idempotency_alias,
        context,
        callable,
        type_t=type,
        at_most_once=False,
    )


@overload
async def until_at_most_once(
    idempotency_alias: str,
    context: WorkflowContext,
    callable: Callable[[], Awaitable[bool]],
    *,
    type: type = bool,
    retryable_exceptions: Optional[list[type[Exception]]] = None,
    # TODO: idempotency_lifetime: Optional[...] = None,
) -> bool:
    ...


@overload
async def until_at_most_once(
    idempotency_alias: str,
    context: WorkflowContext,
    callable: Callable[[], Awaitable[T]],
    *,
    type: type[T],
    retryable_exceptions: Optional[list[type[Exception]]] = None,
    # TODO: idempotency_lifetime: Optional[...] = None,
) -> T:
    ...


async def until_at_most_once(
    idempotency_alias: str,
    context: WorkflowContext,
    callable: Callable[[], Awaitable[T]],
    *,
    type: type = bool,
    retryable_exceptions: Optional[list[type[Exception]]] = None,
    # TODO: idempotency_lifetime: Optional[...] = None,
) -> T:
    """Composition of `until` and `at_least_once`. Attempts to reactively
    run `callable` via `until` and then memoizes that it has been run.
    """

    async def converge():
        return await until(context, callable)

    return await at_most_once(
        idempotency_alias,
        context,
        converge,
        type=type,
        retryable_exceptions=retryable_exceptions,
    )


@overload
async def until_at_least_once(
    idempotency_alias: str,
    context: WorkflowContext,
    callable: Callable[[], Awaitable[bool]],
    *,
    type: type = bool,
    # TODO: idempotency_lifetime: Optional[...] = None,
) -> bool:
    ...


@overload
async def until_at_least_once(
    idempotency_alias: str,
    context: WorkflowContext,
    callable: Callable[[], Awaitable[T]],
    *,
    type: type[T],
    # TODO: idempotency_lifetime: Optional[...] = None,
) -> T:
    ...


async def until_at_least_once(
    idempotency_alias: str,
    context: WorkflowContext,
    callable: Callable[[], Awaitable[T]],
    *,
    type: type = bool,
    # TODO: idempotency_lifetime: Optional[...] = None,
) -> T:
    """Composition of `until` and `at_least_once`. Attempts to reactively
    run `callable` via `until` and then memoizes that it has been run.
    """

    async def converge():
        return await until(context, callable)

    return await at_least_once(
        idempotency_alias,
        context,
        converge,
        type=type,
    )


class MemoizeServicer(AppInternalAuth, Memoize.Interface):

    async def Reset(
        self,
        context: WriterContext,
        state: Memoize.State,
        request: ResetRequest,
    ) -> ResetResponse:
        assert not state.stored
        state.CopyFrom(Memoize.State())
        return ResetResponse()

    async def Status(
        self,
        context: ReaderContext,
        state: Memoize.State,
        request: StatusRequest,
    ) -> StatusResponse:
        return StatusResponse(
            started=state.started,
            stored=state.stored,
            data=state.data,
        )

    async def Start(
        self,
        context: WriterContext,
        state: Memoize.State,
        request: StartRequest,
    ) -> StartResponse:
        assert not state.started
        state.started = True
        return StartResponse()

    async def Store(
        self,
        context: WriterContext,
        state: Memoize.State,
        request: StoreRequest,
    ) -> Memoize.StoreEffects:
        assert not state.stored
        state.stored = True
        state.data = request.data
        return StoreResponse()


def servicers():
    return [MemoizeServicer]
