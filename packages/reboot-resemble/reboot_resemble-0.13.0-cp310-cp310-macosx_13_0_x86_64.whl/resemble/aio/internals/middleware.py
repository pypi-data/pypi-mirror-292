import functools
import grpc
import uuid
from abc import ABC, abstractmethod
from contextlib import contextmanager
from datetime import datetime, timedelta
from google.protobuf.message import Message
from logging import Logger
from resemble.aio.auth.authorizers import Authorizer
from resemble.aio.auth.token_verifiers import TokenVerifier
from resemble.aio.contexts import (
    Context,
    ContextT,
    EffectValidation,
    EffectValidationRetry,
    TransactionContext,
    WorkflowContext,
)
from resemble.aio.headers import Headers
from resemble.aio.idempotency import IdempotencyManager
from resemble.aio.internals.channel_manager import _ChannelManager
from resemble.aio.internals.contextvars import Servicing, _servicing
from resemble.aio.internals.tasks_dispatcher import TasksDispatcher
from resemble.aio.placement import PlacementClient
from resemble.aio.tasks import Loop, TaskEffect
from resemble.aio.types import (
    ApplicationId,
    ConsensusId,
    ServiceName,
    StateRef,
)
from resemble.settings import DOCS_BASE_URL
from typing import (
    Any,
    AsyncIterator,
    Callable,
    Concatenate,
    Coroutine,
    Iterator,
    Optional,
    ParamSpec,
    TypeVar,
)

P = ParamSpec('P')
SelfT = TypeVar('SelfT')
ReturnT = TypeVar('ReturnT')

# Print effect validation warnings every 5 minutes.
_PRINT_EFFECT_VALIDATION_WARNINGS_DELTA = timedelta(minutes=5)

# Dictionary 'method_name': 'timestamp' to keep track of when we last explained
# effect validation. We will warn a user with a message on the first invocation
# of 'method_name' or if a timestamp is older than
# '_PRINT_EFFECT_VALIDATION_WARNINGS_DELTA' minutes.
_has_ever_explained_effect_validation = {}


def maybe_run_function_twice_to_validate_effects(
    f: Callable[Concatenate[bool, P], Coroutine[Any, Any, ReturnT]]
) -> Callable[P, Coroutine[Any, Any, ReturnT]]:
    # TODO: Ideally this would inject a keyword argument, but that cannot currently be made
    # typesafe. See https://peps.python.org/pep-0612/#concatenating-keyword-parameters

    @functools.wraps(f)
    async def wrapper(*args: P.args, **kwargs: P.kwargs):
        try:
            return await f(False, *args, **kwargs)
        except EffectValidationRetry:
            return await f(True, *args, **kwargs)

    return wrapper


class Middleware(ABC):
    """Base class for generated middleware.
    """
    # We expect these values to be set by generated subclass constructors.
    tasks_dispatcher: TasksDispatcher
    request_type_by_method_name: dict[str, type[Message]]

    _token_verifier: Optional[TokenVerifier]
    _authorizer: Optional[Authorizer]

    def __init__(
        self,
        *,
        application_id: ApplicationId,
        consensus_id: ConsensusId,
        service_name: ServiceName,
        placement_client: PlacementClient,
        channel_manager: _ChannelManager,
        effect_validation: EffectValidation,
        app_internal_api_key_secret: str,
    ):
        self._application_id = application_id
        self._consensus_id = consensus_id
        self._service_name = service_name
        self._effect_validation = effect_validation
        self._app_internal_api_key_secret = app_internal_api_key_secret

        self.placement_client = placement_client
        self.channel_manager = channel_manager

    @property
    def application_id(self) -> ApplicationId:
        return self._application_id

    @property
    def consensus_id(self) -> ConsensusId:
        return self._consensus_id

    @property
    def service_name(self) -> ServiceName:
        return self._service_name

    def create_context(
        self,
        *,
        headers: Headers,
        context_type: type[ContextT],
        task: Optional[TaskEffect] = None,
    ) -> ContextT:
        """Create a Context object given the parameters."""
        # Toggle 'servicing' to indicate we are initializing the
        # servicing of an RPC which will, for example, permit the
        # construction of a context without raising an error.
        _servicing.set(Servicing.INITIALIZING)

        # Sanity check: we're handling the right type, right?
        if headers.service_name != self._service_name:
            raise ValueError(
                f'Requested unexpected service name {headers.service_name}; '
                f'this servicer is of type {self._service_name}'
            )

        context = context_type(
            channel_manager=self.channel_manager,
            headers=headers,
            app_internal_api_key_secret=self._app_internal_api_key_secret,
            task=task,
        )

        # Now toggle 'servicing' to indicate that we are servicing the
        # RPC which will, for example, forbid the construction of a
        # context by raising an error.
        _servicing.set(Servicing.YES)

        return context

    @contextmanager
    def use_context(
        self,
        *,
        headers: Headers,
        context_type: type[ContextT],
        task: Optional[TaskEffect] = None,
    ) -> Iterator[ContextT]:
        """Context manager for ensuring that we reset the asyncio context
        variable to the previous context.
        """
        context: Optional[Context] = Context.get()
        try:
            yield self.create_context(
                headers=headers,
                context_type=context_type,
                task=task,
            )
        finally:
            if context is not None:
                Context.set(context)

    async def stop(self):
        """Stop the middleware background tasks.
        """
        await self.tasks_dispatcher.stop()

    def _print_info_message_for_effect_validation(
        self,
        method_name: str,
    ) -> bool:
        if self._effect_validation == EffectValidation.QUIET:
            if method_name not in _has_ever_explained_effect_validation:
                _has_ever_explained_effect_validation[method_name
                                                     ] = datetime.now()
                return True
            last_printed = _has_ever_explained_effect_validation[method_name]
            if datetime.now(
            ) - last_printed > _PRINT_EFFECT_VALIDATION_WARNINGS_DELTA:
                _has_ever_explained_effect_validation[method_name
                                                     ] = datetime.now()
                return True
            return False
        return True

    def maybe_raise_effect_validation_retry(
        self,
        *,
        logger: Logger,
        idempotency_manager: IdempotencyManager,
        method_name: str,
        validating_effects: bool,
        context: Context,
    ) -> None:
        """If we're validating effects, explains that we are about to retry, and then raises.
        """
        if self._effect_validation == EffectValidation.DISABLED or validating_effects:
            # Effect validation is disabled, or we are in the second run of an effect
            # validation: either way, allow the method to complete.
            return

        is_non_root_in_nested = (
            # Is either an inner method in a transaction, or a nested transaction.
            (
                not isinstance(context, TransactionContext) and
                context.transaction_id is not None
            ) or
            (isinstance(context, TransactionContext) and context.nested) or
            # Is an inner method in a workflow.
            (
                not isinstance(context, WorkflowContext) and
                context.workflow_id is not None
            )
        )
        if is_non_root_in_nested:
            # When a method is nested (transactions/workflows), retry occurs
            # only at the top level. This is a non-root method below a nested
            # method, so don't retry.
            return

        # Effect validation is enabled, and this method needs to retry: compose
        # a message, log it, and then raise.
        message = (
            f"Re-running method {method_name} to validate effects. "
            f"See {DOCS_BASE_URL}/develop/side_effects for "
            "more information."
        )

        if self._print_info_message_for_effect_validation(method_name):
            # Silence only in the 'QUIET' mode.
            if self._effect_validation == EffectValidation.QUIET:
                logger.info(
                    f"{message} Will silence this message for the next "
                    f"{_PRINT_EFFECT_VALIDATION_WARNINGS_DELTA.seconds // 60} minutes."
                )
            else:
                logger.info(message)
        else:
            logger.debug(message)

        # Reset the `IdempotencyManager` so that we re-execute the
        # method as though it is being retried from scratch.
        idempotency_manager.reset()

        raise EffectValidationRetry()

    @abstractmethod
    async def dispatch(
        self,
        task: TaskEffect,
        *,
        only_validate: bool = False,
    ) -> Message | Loop:
        """Abstract dispatch method; implemented by code generation for each
        of the service's task methods."""
        raise NotImplementedError

    @abstractmethod
    async def inspect(self, state_ref: StateRef) -> AsyncIterator[Message]:
        """Abstract method for handling an Inspect request; implemented by code
        generation for each of the services."""
        raise NotImplementedError
        yield  # Necessary for type checking.

    @abstractmethod
    async def react_query(
        self,
        grpc_context: grpc.aio.ServicerContext,
        headers: Headers,
        method: str,
        request_bytes: bytes,
    ) -> AsyncIterator[tuple[Optional[Message], list[uuid.UUID]]]:
        """Abstract method for handling a React request; implemented by code
        generation for each of the service's React compatible reader methods."""
        raise NotImplementedError
        yield  # Necessary for type checking.

    @abstractmethod
    async def react_mutate(
        self,
        headers: Headers,
        method: str,
        request_bytes: bytes,
    ) -> Message:
        """Abstract method for handling a React mutation; implemented by code
        generation for each of the service's React compatible mutator methods."""
        raise NotImplementedError

    @abstractmethod
    def add_to_server(self, server: grpc.aio.Server) -> None:
        raise NotImplementedError
