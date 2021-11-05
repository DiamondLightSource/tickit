import asyncio
from time import time_ns
from typing import Type, Union

from tickit.core.management.event_router import InverseWiring, Wiring
from tickit.core.management.schedulers.base import BaseScheduler
from tickit.core.state_interfaces.state_interface import StateConsumer, StateProducer
from tickit.core.typedefs import ComponentID, SimTime


class MasterScheduler(BaseScheduler):
    """A master scheduler which orchestrates the running of a tickit simulation."""

    def __init__(
        self,
        wiring: Union[Wiring, InverseWiring],
        state_consumer: Type[StateConsumer],
        state_producer: Type[StateProducer],
        initial_time: int = 0,
        simulation_speed: float = 1.0,
    ) -> None:
        """A master scheduler constructor  which stores values for reference.

        Args:
            wiring (Union[Wiring, InverseWiring]): A wiring or inverse wiring object
                representing the connections between components in the system.
            state_consumer (Type[StateConsumer]): The state consumer class to be used
                by the component.
            state_producer (Type[StateProducer]): The state producer class to be used
                by the component.
            initial_time (int): The initial time of the simulation (in nanoseconds).
                Defaults to 0.
            simulation_speed (float): The rate at which simulation time progresses with
                respect to real world time. Defaults to 1.0.
        """
        super().__init__(wiring, state_consumer, state_producer)

        self._initial_time = SimTime(initial_time)
        self.simulation_speed = simulation_speed

    async def setup(self) -> None:
        """Performs base setup and creates an awaitable flag to indicate new wakeups."""
        await super().setup()
        self.new_wakeup: asyncio.Event = asyncio.Event()

    def add_wakeup(self, component: ComponentID, when: SimTime) -> None:
        """Adds a wakeup to the priority queue and sets an awaitable flag.

        A method which adds a wakeup to the priority queue and sets a awaitable flag
        indicating that a new wakeup has been added.

        Args:
            component (ComponentID): The component which should be updated.
            when (SimTime): The simulation time at which the update should occur.
        """
        super().add_wakeup(component, when)
        self.new_wakeup.set()

    async def run_forever(self) -> None:
        """Performs an intial tick then continiously schedules ticks according to wakeups.

        An asynchronous method which initially performs setup and an initial tick in
        which all components are updated, subsequently ticks are performed as requested
        by components of the simulation according to the simulation speed.
        """
        await self.setup()
        await self._do_initial_tick()
        while True:
            await self._do_tick()

    async def _do_initial_tick(self):
        """Performs the initial tick of the system."""
        await self.ticker(
            self._initial_time,
            self.ticker.components,
        )
        self.last_time = time_ns()

    async def _do_tick(self):
        """Continuously schedules ticks according to wakeups."""
        if not self.wakeups:
            await self.new_wakeup.wait()
        components, when = self.get_first_wakeups()
        assert when is not None
        self.new_wakeup.clear()

        current: asyncio.Future = asyncio.sleep(self.sleep_time(when))
        new = asyncio.create_task(self.new_wakeup.wait())
        which, _ = await asyncio.wait(
            [current, new], return_when=asyncio.tasks.FIRST_COMPLETED
        )

        if new in which:
            return

        for component in components:
            del self.wakeups[component]
        await self.ticker(when, {component for component in components})
        self.last_time = time_ns()

    async def schedule_interrupt(self, source: ComponentID) -> None:
        """Schedules the interrupt of a component immediately.

        An asynchronous method which implements the superclass abstract, an interrupt
        is sheduled as an immediate wakeup. This is achieved by giving the wakeup a
        simulation time equal to the simulation time of the last tick plus the real
        world time which has passed, adjusted by the simulation speed.

        Args:
            source (ComponentID): The source component which should be updated.
        """
        self.add_wakeup(
            source,
            SimTime(
                self.ticker.time
                + int((time_ns() - self.last_time) * self.simulation_speed)
            ),
        )

    def sleep_time(self, when: SimTime) -> float:
        """Computes the real world time until a specified simulation time.

        Args:
            when (SimTime): The simulation time to be reached.

        Returns:
            float: The real world duration before the simulation time is reached.
        """
        return (
            (when - self.ticker.time) / self.simulation_speed
            - (time_ns() - self.last_time)
        ) / 1e9
