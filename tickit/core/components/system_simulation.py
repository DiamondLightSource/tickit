from typing import Dict, List, Tuple, Type

from tickit.core.components.component import (
    BaseComponent,
    ComponentConfig,
    create_components,
)
from tickit.core.management.event_router import InverseWiring
from tickit.core.management.schedulers.slave import SlaveScheduler
from tickit.core.state_interfaces.state_interface import StateConsumer, StateProducer
from tickit.core.typedefs import Changes, ComponentID, PortID, SimTime


class SystemSimulation(BaseComponent):
    def __init__(
        self,
        name: ComponentID,
        components: List[ComponentConfig],
        state_consumer: Type[StateConsumer],
        state_producer: Type[StateProducer],
        expose: Dict[PortID, Tuple[ComponentID, PortID]],
    ) -> None:
        super().__init__(name, state_consumer, state_producer)
        inverse_wiring = InverseWiring.from_component_configs(components)
        self.scheduler = SlaveScheduler(
            inverse_wiring,
            state_consumer,
            state_producer,
            expose,
            self.raise_interrupt,
        )
        self.component_simulations = create_components(
            components, state_consumer, state_producer
        )

    async def run_forever(self):
        for component_simulation in self.component_simulations:
            await component_simulation.run_forever()
        await self.scheduler.run_forever()
        await super().set_up_state_interfaces()

    async def on_tick(self, time: SimTime, changes: Changes) -> None:
        output_changes, call_in = await self.scheduler.on_tick(time, changes)
        await self.output(time, output_changes, call_in)
