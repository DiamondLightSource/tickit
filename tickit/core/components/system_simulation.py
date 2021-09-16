import asyncio
from typing import Dict, List, Type

from tickit.core.components.component import (
    BaseComponent,
    ComponentConfig,
    create_components,
)
from tickit.core.lifetime_runnable import run_all
from tickit.core.management.event_router import InverseWiring
from tickit.core.management.schedulers.slave import SlaveScheduler
from tickit.core.state_interfaces.state_interface import StateConsumer, StateProducer
from tickit.core.typedefs import Changes, ComponentID, ComponentPort, PortID, SimTime


class SystemSimulation(BaseComponent):
    """A component containing a slave scheduler and several components.

    A component which acts as a nested tickit simulation by wrapping a slave scheduler
    and a set of internal components, this component delegates core behaviour to the
    components within it, whilst outputting their requests for wakeups and interrupts.
    """

    def __init__(
        self,
        name: ComponentID,
        components: List[ComponentConfig],
        state_consumer: Type[StateConsumer],
        state_producer: Type[StateProducer],
        expose: Dict[PortID, ComponentPort],
    ) -> None:
        """A constructor which creates component simulations and adds exposing wiring.

        Args:
            name (ComponentID): The unique identifier of the system simulation.
            components (List[ComponentConfig]): A list of immutable component
                configuration data containers, used to construct internal components.
            state_consumer (Type[StateConsumer]): The state consumer class to be used
                by the component.
            state_producer (Type[StateProducer]): The state producer class to be used
                by the component.
            expose (Dict[PortID, ComponentPort]): A mapping of outputs which
                the system simulation exposes and the corresponding output of an
                internal component.
        """
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
        """Sets up state interfaces, the scheduler and components and blocks until any complete.

        An asynchronous method starts the run_forever method of each component, runs
        the scheduler, and sets up externally facing state interfaces. The method
        blocks until and of the components or the scheduler complete.
        """
        tasks = run_all((*self.component_simulations, self.scheduler))
        await self.set_up_state_interfaces()
        await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

    async def on_tick(self, time: SimTime, changes: Changes) -> None:
        """Delegates core behaviour to the slave scheduler.

        An asynchronous method which delegates core behaviour of computing changes and
        determining a callback period to the slave shceduler and sends the resulting
        Output.

        Args:
            time (SimTime): The current simulation time (in nanoseconds).
            changes (Changes): A mapping of changed component inputs and their new
                values.
        """
        output_changes, call_in = await self.scheduler.on_tick(time, changes)
        await self.output(time, output_changes, call_in)
