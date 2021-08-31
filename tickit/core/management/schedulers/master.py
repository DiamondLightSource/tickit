import asyncio
from time import time_ns
from typing import Type, Union

from tickit.core.management.event_router import InverseWiring, Wiring
from tickit.core.management.schedulers.base import BaseScheduler
from tickit.core.state_interfaces.state_interface import StateConsumer, StateProducer
from tickit.core.typedefs import ComponentID, SimTime


class MasterScheduler(BaseScheduler):
    def __init__(
        self,
        wiring: Union[Wiring, InverseWiring],
        state_consumer: Type[StateConsumer],
        state_producer: Type[StateProducer],
        initial_time: int = 0,
        simulation_speed: float = 1.0,
    ) -> None:
        super().__init__(wiring, state_consumer, state_producer)

        self._initial_time = SimTime(initial_time)
        self.simulation_speed = simulation_speed

    async def setup(self) -> None:
        await super().setup()
        self.new_wakeup: asyncio.Event = asyncio.Event()

    async def add_wakeup(self, component: ComponentID, when: SimTime) -> None:
        await super().add_wakeup(component, when)
        self.new_wakeup.set()

    async def run_forever(self) -> None:
        await self.setup()
        await self.ticker(
            self._initial_time, self.ticker.components,
        )
        self.last_time = time_ns()
        while True:
            _, wakeups = await self.wakeups.get_all_tie()
            self.new_wakeup.clear()

            current: asyncio.Future = asyncio.sleep(self.sleep_time(wakeups[0].when))
            new = asyncio.create_task(self.new_wakeup.wait())
            which, _ = await asyncio.wait(
                {current, new}, return_when=asyncio.tasks.FIRST_COMPLETED
            )

            if new in which:
                await self.wakeups.put_many((wakeup.when, wakeup) for wakeup in wakeups)
                continue

            await self.ticker(wakeups[0].when, {wakeup.component for wakeup in wakeups})
            self.last_time = time_ns()

    async def schedule_interrupt(self, source: ComponentID) -> None:
        await self.add_wakeup(
            source,
            SimTime(
                self.ticker.time
                + int((time_ns() - self.last_time) * self.simulation_speed)
            ),
        )

    def sleep_time(self, when: SimTime) -> float:
        return (
            (when - self.ticker.time) / self.simulation_speed
            - (time_ns() - self.last_time)
        ) / 1e9
