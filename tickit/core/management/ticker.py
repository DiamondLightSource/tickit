import asyncio
import logging
from collections import defaultdict
from typing import (
    Awaitable,
    Callable,
    DefaultDict,
    Dict,
    Hashable,
    Optional,
    Set,
    Union,
)

from immutables import Map

from tickit.core.management.event_router import EventRouter, InverseWiring, Wiring
from tickit.core.typedefs import Changes, ComponentID, Input, Output, PortID, SimTime

LOGGER = logging.getLogger(__name__)


class Ticker:
    """A utility class responsible for sequencing the update of components during a tick.

    A utility class responsible for sequencing the update of components during a tick
    by eagerly updating each component which has had all of its dependencies resolved.
    """

    def __init__(
        self,
        wiring: Union[Wiring, InverseWiring],
        update_component: Callable[[Input], Awaitable[None]],
    ) -> None:
        """A Ticker constructor which creates an event router and performs initial setup.

        Args:
            wiring (Union[Wiring, InverseWiring]): A wiring or inverse wiring object
                representing the connections between components in the system.
            update_component (Callable[[Input], Awaitable[None]]): A function or method
                which may be called to request a component performs and update, such
                updates should result in a subsequent call to the propagate method of
                the ticker.
        """
        self.event_router = EventRouter(wiring)
        self.update_component = update_component
        self.to_update: Dict[ComponentID, Optional[asyncio.Task]] = dict()
        self.finished: asyncio.Event = asyncio.Event()

    async def __call__(
        self, time: SimTime, update_components: Set[ComponentID]
    ) -> None:
        """Performs a tick which updates the provided components and their dependants.

        An asynchronous method which performs a tick by setting up the initial state of
        the system during the tick - including determining dependant components,
        scheduling updates which require no component resolutions to be performed,
        before blocking until the system is resolved by update propagation.

        Args:
            time (SimTime): The simulation time at which the tick occurs (in
                nanoseconds).
            update_components (Set[ComponentID]): A set of components which require
                update.
        """
        await self._start_tick(time, update_components)
        await self.schedule_possible_updates()
        await self.finished.wait()
        self.finished.clear()

    async def _start_tick(self, time: SimTime, update_components: Set[ComponentID]):
        """Sets up the ticker to perform a tick.

        An asynchronous method which sets up the ticker to perform a tick by updating
        time, reseting accumulators and finding the set of components which require
        update.

        Args:
            time (SimTime): The simulation time at which the tick occurs (in
                nanoseconds).
            update_components (Set[ComponentID]): A set of components which require
                update.
        """
        self.time = time
        self.roots = update_components
        LOGGER.debug("Doing tick @ {}".format(self.time))
        self.inputs: DefaultDict[ComponentID, Dict[PortID, Hashable]] = defaultdict(
            dict
        )
        self.to_update = {
            c: None
            for component in self.roots
            for c in self.event_router.dependants(component)
        }

    async def schedule_possible_updates(self) -> None:
        """Updates components with resolved dependencies.

        An asynchronous method which schedules updates for components with resolved
        dependencies, as determined by the intersection of the components first order
        dependencies and the set of componets which still require an update.
        """

        def required_dependencies(component) -> Set[ComponentID]:
            return self.event_router.inverse_component_tree[component].intersection(
                self.to_update
            )

        updating: Dict[ComponentID, asyncio.Task] = dict()
        skipping: Set[ComponentID] = set()
        for component, task in self.to_update.items():
            if task is not None or required_dependencies(component):
                continue
            if self.inputs[component] or component in self.roots:
                updating[component] = asyncio.create_task(
                    self.update_component(
                        Input(
                            component, self.time, Changes(Map(self.inputs[component]))
                        )
                    )
                )
            else:
                skipping.add(component)
        self.to_update.update(updating)
        for component in skipping:
            del self.to_update[component]

    async def propagate(self, output: Output) -> None:
        """Propagates the output of an updated component.

        An asynchronous message which propagates the output of an updated component by
        removing the component from the set of components requiring update, adding the
        routed inputs to the accumulator, and scheduling any possible updates. If no
        components require update the finsihed flag will be set.

        Args:
            output (Output): The output produced by the update of a component.
        """
        assert output.source in self.to_update.keys()
        assert output.time == self.time
        self.to_update.pop(output.source)

        changes = self.event_router.route(output.source, output.changes)
        for component, change in changes.items():
            self.inputs[component].update(change)

        await self.schedule_possible_updates()
        if not self.to_update:
            self.finished.set()

    @property
    def components(self) -> Set[ComponentID]:
        """The set of all components in the wiring.

        Returns:
            Set[ComponentID]: The set of all components in the wiring.
        """
        return self.event_router.components
