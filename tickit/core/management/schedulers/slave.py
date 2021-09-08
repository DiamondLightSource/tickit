from typing import Awaitable, Callable, Dict, Optional, Set, Tuple, Type, Union

from immutables import Map

from tickit.core.management.event_router import InverseWiring, Wiring
from tickit.core.management.schedulers.base import BaseScheduler
from tickit.core.state_interfaces.state_interface import StateConsumer, StateProducer
from tickit.core.typedefs import Changes, ComponentID, Input, Output, PortID, SimTime


class SlaveScheduler(BaseScheduler):
    def __init__(
        self,
        wiring: Union[Wiring, InverseWiring],
        state_consumer: Type[StateConsumer],
        state_producer: Type[StateProducer],
        expose: Dict[PortID, Tuple[ComponentID, PortID]],
        raise_interrupt: Callable[[], Awaitable[None]],
    ) -> None:
        wiring = self.add_exposing_wiring(wiring, expose)
        super().__init__(wiring, state_consumer, state_producer)
        self.raise_interrupt = raise_interrupt
        self.interrupts: Set[ComponentID] = set()

    @staticmethod
    def add_exposing_wiring(
        wiring: Union[Wiring, InverseWiring],
        expose: Dict[PortID, Tuple[ComponentID, PortID]],
    ) -> InverseWiring:
        if isinstance(wiring, Wiring):
            wiring = InverseWiring.from_wiring(wiring)
        wiring[ComponentID("expose")].update(expose)
        return wiring

    async def update_component(self, input: Input) -> None:
        if input.target == ComponentID("external"):
            await self.ticker.propagate(
                Output(ComponentID("external"), input.time, self.input_changes, None)
            )
        elif input.target == ComponentID("expose"):
            self.output_changes = input.changes
            await self.ticker.propagate(
                Output(ComponentID("expose"), input.time, Changes(Map()), None)
            )
        else:
            await super().update_component(input)

    async def on_tick(
        self, time: SimTime, changes: Changes
    ) -> Tuple[Changes, Optional[SimTime]]:

        root_components: Set[ComponentID] = {
            *self.interrupts,
            *(wakeup.component for wakeup in await self.wakeups.all_lt(time)),
            ComponentID("external"),
        }
        self.interrupts.clear()

        self.input_changes = changes
        self.output_changes = Changes(Map())
        await self.ticker(time, root_components)

        call_in = None
        if not self.wakeups.empty():
            priority, wakeup = await self.wakeups.get()
            call_in = SimTime(wakeup.when - time)
            self.wakeups.put((priority, wakeup))

        return self.output_changes, call_in

    async def run_forever(self) -> None:
        await self.setup()

    async def schedule_interrupt(self, source: ComponentID) -> None:
        print("Adding {} to interrupts".format(source))
        self.interrupts.add(source)
        await self.raise_interrupt()
