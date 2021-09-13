import asyncio
import logging
from typing import Awaitable, Callable, Dict, Optional, Set, Union

from immutables import Map

from tickit.core.management.event_router import EventRouter, InverseWiring, Wiring
from tickit.core.typedefs import Changes, ComponentID, Input, Output, SimTime

LOGGER = logging.getLogger(__name__)


class Ticker:
    def __init__(
        self,
        wiring: Union[Wiring, InverseWiring],
        update_component: Callable[[Input], Awaitable[None]],
    ) -> None:
        self.event_router = EventRouter(wiring)
        self.update_component = update_component
        self.to_update: Dict[ComponentID, Optional[asyncio.Task]] = dict()
        self.finished: asyncio.Event = asyncio.Event()

    async def __call__(
        self, time: SimTime, update_components: Set[ComponentID]
    ) -> None:
        await self._start_tick(time, update_components)
        await self.schedule_possible_updates()
        await self.finished.wait()
        self.finished.clear()

    async def _start_tick(self, time: SimTime, update_components: Set[ComponentID]):
        self.time = time
        LOGGER.debug("Doing tick @ {}".format(self.time))
        self.inputs: Set[Input] = set()
        self.to_update = {
            c: None
            for component in update_components
            for c in self.event_router.dependants(component)
        }

    async def schedule_possible_updates(self) -> None:
        self.to_update.update(
            {
                component: asyncio.create_task(
                    self.update_component(
                        self.collate_inputs(self.inputs, component, self.time)
                    )
                )
                for component, task in self.to_update.items()
                if task is None
                and not self.event_router.inverse_component_tree[
                    component
                ].intersection(self.to_update)
            }
        )

    def collate_inputs(
        self, inputs: Set[Input], component: ComponentID, time: SimTime
    ) -> Input:
        return Input(
            component,
            time,
            Changes(
                Map(
                    {
                        k: v
                        for input in inputs
                        if input.target == component and input.time == time
                        for k, v in input.changes.items()
                    }
                )
            ),
        )

    async def propagate(self, output: Output) -> None:
        assert output.source in self.to_update.keys()
        assert output.time == self.time
        self.to_update.pop(output.source)
        self.inputs.update(self.event_router.route(output))
        await self.schedule_possible_updates()
        if not self.to_update:
            self.finished.set()

    @property
    def components(self) -> Set[ComponentID]:
        return self.event_router.components
