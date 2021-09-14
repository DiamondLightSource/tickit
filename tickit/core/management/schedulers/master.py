import asyncio
from time import time_ns
from typing import Type, Union

from tickit.core.management.event_router import InverseWiring, Wiring
from tickit.core.management.schedulers.base import BaseScheduler
from tickit.core.state_interfaces.state_interface import StateConsumer, StateProducer
from tickit.core.typedefs import ComponentID, SimTime


class MasterScheduler(BaseScheduler):
    """A master scheduler which orchestrates the running of a tickit simulation"""

    def __init__(
        self,
        wiring: Union[Wiring, InverseWiring],
        state_consumer: Type[StateConsumer],
        state_producer: Type[StateProducer],
        initial_time: int = 0,
        simulation_speed: float = 1.0,
    ) -> None:
        """A constructor of the master sheduler which stores values for reference

        Args:
            wiring (Union[Wiring, InverseWiring]): A wiring or inverse wiring object
                representing the connections between components in the system
            state_consumer (Type[StateConsumer]): The state consumer class to be used
                by the component
            state_producer (Type[StateProducer]): The state producer class to be used
                by the component
            initial_time (int): The initial time of the simulation (in nanoseconds).
                Defaults to 0.
            simulation_speed (float): The rate at which simulation time progresses with
                respect to real world time. Defaults to 1.0.
        """
        super().__init__(wiring, state_consumer, state_producer)

        self._initial_time = SimTime(initial_time)
        self.simulation_speed = simulation_speed

    async def setup(self) -> None:
        """An asynchronous method which does base setup and creates a new wakeup flag"""
        await super().setup()
        self.new_wakeup: asyncio.Event = asyncio.Event()

    async def add_wakeup(self, component: ComponentID, when: SimTime) -> None:
        """An asynchronous method which adds a wakeup to the priority queue and sets a flag

        An asynchronous method which adds a wakeup to the priority queue and sets a
        flag indicating that a new wakeup has been added

        Args:
            component (ComponentID): The component which should be updated
            when (SimTime): The simulation time at which the update should occur
        """
        await super().add_wakeup(component, when)
        self.new_wakeup.set()

    async def run_forever(self) -> None:
        """An asynchronous method which continiously schedules ticks as requested

        An asynchronous method which initially performs setup and an initial tick in
        which all components are updated, subsequently ticks are performed as requested
        by components of the simulation according to the simulation speed
        """
        await self.setup()
        await self.ticker(
            self._initial_time,
            self.ticker.components,
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
        """An asynchronous method which schedules an interrupt immediately

        An asynchronous method which implements the superclass abstract, an interrupt
        is sheduled as an immediate wakeup. This is achieved by giving the wakeup a
        simulation time equal to the simulation time of the last tick plus the real
        world time which has passed, adjusted by the simulation speed

        Args:
            source (ComponentID): The component which should be updated
        """
        await self.add_wakeup(
            source,
            SimTime(
                self.ticker.time
                + int((time_ns() - self.last_time) * self.simulation_speed)
            ),
        )

    def sleep_time(self, when: SimTime) -> float:
        """A method which computes the real world time until a specified simulation time

        Args:
            when (SimTime): The simulation time to be reached

        Returns:
            float: The real world duration before the simulation time is reached
        """
        return (
            (when - self.ticker.time) / self.simulation_speed
            - (time_ns() - self.last_time)
        ) / 1e9
