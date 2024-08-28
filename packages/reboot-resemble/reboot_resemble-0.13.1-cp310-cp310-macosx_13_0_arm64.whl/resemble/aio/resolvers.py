import asyncio
from abc import ABC, abstractmethod
from resemble.aio.placement import PlacementClient
from resemble.aio.servicers import Servicer
from resemble.aio.types import (
    ApplicationId,
    RoutableAddress,
    ServiceName,
    StateRef,
)
from respect.logging import get_logger
from typing import Iterable, Optional

logger = get_logger(__name__)


class ActorResolver(ABC):
    """Abstract base class for a resolver able to resolve an actor id and
    service name into a routable address.
    """

    @abstractmethod
    def resolve_actor(
        self,
        service_name: ServiceName,
        state_ref: StateRef,
    ) -> Optional[RoutableAddress]:
        """Get routable address for actor."""
        # This function is not allowed to block.
        # ISSUE(#1178): This function is deliberately not async.
        pass

    def resolve(
        self,
        servicer_type: type[Servicer],
        state_ref: StateRef,
    ) -> Optional[RoutableAddress]:
        """Get routable address for actor."""
        return self.resolve_actor(servicer_type.__service_name__, state_ref)

    @abstractmethod
    async def wait_for_service_names(
        self,
        service_names: Iterable[ServiceName],
    ):
        """Returns once the resolver knows about all the service names, which
        may be immediately.
        """
        pass

    async def wait_for_servicers(self, servicers: Iterable[type[Servicer]]):
        """Syntactic sugar for wait_for_service_names that takes `Servicer`s.
        """
        service_names = [servicer.__service_name__ for servicer in servicers]

        await self.wait_for_service_names(service_names)


class DictResolver(ActorResolver):
    """A dictionary backed resolver.

    Resolves actors based on a dictionary from an service name to a routable
    address.
    """

    def __init__(
        self,
        servicer_dict: Optional[dict[ServiceName, RoutableAddress]] = None,
    ):
        self._actors: dict[ServiceName, RoutableAddress] = servicer_dict or {}
        self._actors_updated_events: list[asyncio.Event] = []

    def resolve_actor(
        self,
        service_name: ServiceName,
        state_ref: StateRef,
    ) -> Optional[RoutableAddress]:
        """Resolve actor using internal dictionary. The actor id is unused."""
        return self._actors.get(service_name)

    def update(self, update: dict[ServiceName, RoutableAddress]) -> None:
        """Update the internal dictionary with items from the input."""
        self._actors.update(update)
        for event in self._actors_updated_events:
            event.set()

    async def wait_for_service_names(
        self,
        service_names: Iterable[ServiceName],
    ):
        """Override of `ActorResolver.wait_for_service_names`."""
        event = asyncio.Event()
        try:
            self._actors_updated_events.append(event)
            while not all(
                service_name in self._actors for service_name in service_names
            ):
                await event.wait()
                event.clear()
        finally:
            self._actors_updated_events.remove(event)


class DirectResolver(ActorResolver):
    """
    A resolver that listens directly to a PlacementPlanner to learn about actors
    and their addresses.

    Primarily expected to be useful in unit tests, where more sophisticated (and
    scalable) mechanisms like using an Envoy routing filter are unavailable.

    ISSUE(https://github.com/reboot-dev/respect/issues/3225): DirectResolver may
         only be used in environments where every `ServiceName` is unique across
         all applications, notably unit tests and single-application
         deployments.
    """

    def __init__(self, placement_client: PlacementClient):
        self._placement_client = placement_client

    def application_id_by_service_name(
        self
    ) -> dict[ServiceName, ApplicationId]:
        # ASSUMPTION: DirectResolver is only used in environments where every
        #             `ServiceName` is unique to a SINGLE application. See
        #             classdoc above.
        result: dict[ServiceName, ApplicationId] = {}
        for application_id in self._placement_client.known_application_ids():
            for service_name in self._placement_client.known_service_names(
                application_id
            ):
                assert service_name not in result, "ASSUMPTION (see comment) violated"
                result[service_name] = application_id

        return result

    def resolve_actor(
        self,
        service_name: ServiceName,
        state_ref: StateRef,
    ) -> Optional[RoutableAddress]:
        """Finds the routable address for the given actor id on the given
        service."""

        # Determine the application ID based on the `ServiceName`.
        #
        # ASSUMPTION: DirectResolver is only used in environments where every
        #             `ServiceName` is unique to a SINGLE application. See
        #             classdoc above.
        application_id = self.application_id_by_service_name(
        ).get(service_name)
        if application_id is None:
            return None

        return self._placement_client.address_for_actor(
            application_id, service_name, state_ref
        )

    async def wait_for_service_names(
        self,
        service_names: Iterable[ServiceName],
    ):
        """Override of `ActorResolver.wait_for_service_names`."""
        while True:
            known_service_names = self.application_id_by_service_name().keys()
            if all(
                service_name in known_service_names
                for service_name in service_names
            ):
                break
            await self._placement_client.wait_for_change()

    async def wait_for_change(self):
        await self._placement_client.wait_for_change()

    async def start(self):
        await self._placement_client.start()

    async def stop(self):
        await self._placement_client.stop()


class StaticResolver(ActorResolver):
    """A resolver that always returns the same address for all actors."""

    def __init__(self, address: RoutableAddress):
        self.address = address

    def resolve_actor(
        self,
        service_name: ServiceName,
        state_ref: StateRef,
    ) -> Optional[RoutableAddress]:
        return self.address

    async def wait_for_service_names(
        self, service_names: Iterable[ServiceName]
    ):
        """Override of `ActorResolver.wait_for_service_names`."""
        return
