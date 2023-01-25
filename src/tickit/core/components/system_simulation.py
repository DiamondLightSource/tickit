import asyncio
from dataclasses import dataclass
from typing import Dict, List, Type

from tickit.core.components.component import BaseComponent, Component, ComponentConfig
from tickit.core.management.event_router import InverseWiring
from tickit.core.management.schedulers.slave import SlaveScheduler
from tickit.core.runner import run_all
from tickit.core.state_interfaces.state_interface import StateConsumer, StateProducer
from tickit.core.typedefs import Changes, ComponentID, ComponentPort, PortID, SimTime


@dataclass
class SystemSimulationComponent(BaseComponent):
    """A component containing a slave scheduler and several components.

    A component which acts as a nested tickit simulation by wrapping a slave scheduler
    and a set of internal components, this component delegates core behaviour to the
    components within it, whilst outputting their requests for wakeups and interrupts.
    """

    name: ComponentID

    #: A list of immutable component configuration data containers, used to
    #: construct internal components.
    components: List[ComponentConfig]
    #: A mapping of outputs which the system simulation exposes and the
    #: corresponding output of an internal component.
    expose: Dict[PortID, ComponentPort]

    async def run_forever(
        self, state_consumer: Type[StateConsumer], state_producer: Type[StateProducer]
    ) -> None:
        """Sets up state interfaces, the scheduler and components and blocks until any complete.

        An asynchronous method starts the run_forever method of each component, runs
        the scheduler, and sets up externally facing state interfaces. The method
        blocks until and of the components or the scheduler complete.
        """
        inverse_wiring = InverseWiring.from_component_configs(self.components)
        self.scheduler = SlaveScheduler(
            inverse_wiring,
            state_consumer,
            state_producer,
            self.expose,
            self.raise_interrupt,
        )
        tasks = run_all(
            component().run_forever(state_consumer, state_producer)
            for component in self.components
        ) + run_all([self.scheduler.run_forever()])
        await super().run_forever(state_consumer, state_producer)
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


@dataclass
class SystemSimulation(ComponentConfig):
    """Simulation of a nested set of components."""

    name: ComponentID
    inputs: Dict[PortID, ComponentPort]
    components: List[ComponentConfig]
    expose: Dict[PortID, ComponentPort]

    def __call__(self) -> Component:  # noqa: D102
        return SystemSimulationComponent(
            name=self.name,
            components=self.components,
            expose=self.expose,
        )
