import asyncio
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Type
from tickit.adapters.composed import ComposedAdapter
from tickit.adapters.interpreters.command.command_interpreter import CommandInterpreter
from tickit.adapters.servers.tcp import TcpServer
from tickit.adapters.system_simulation_adapter import SystemSimulationAdapter
from tickit.core.adapter import Adapter

from tickit.core.components.component import BaseComponent, Component, ComponentConfig
from tickit.core.components.system_simulation_view import SystemSimulationView
from tickit.core.management.event_router import InverseWiring
from tickit.core.management.schedulers.slave import SlaveScheduler
from tickit.core.runner import run_all
from tickit.core.state_interfaces.state_interface import StateConsumer, StateProducer
from tickit.core.typedefs import Changes, ComponentID, ComponentPort, PortID, SimTime
from tickit.utils.byte_format import ByteFormat
from tickit.utils.topic_naming import output_topic

LOGGER = logging.getLogger(__name__)


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

    _internal_adapter: Adapter[SystemSimulationView] = SystemSimulationAdapter(
        TcpServer(host="localhost", port=25555, format=ByteFormat(b"%b\r\n")),
        CommandInterpreter(),
    )

    _tasks: List[asyncio.Task] = field(default_factory=list)

    async def run_forever(
        self, state_consumer: Type[StateConsumer], state_producer: Type[StateProducer]
    ) -> None:
        """Sets up state interfaces, the scheduler, and components to run continuously.

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
        components = {config.name: config() for config in self.components}

        self._tasks = run_all(
            component.run_forever(state_consumer, state_producer)
            for component in components.values()
        ) + run_all([self.scheduler.run_forever()])

        if self._internal_adapter:
            self._tasks.append(
                asyncio.create_task(
                    self._internal_adapter.run_forever(
                        SystemSimulationView(self.scheduler._wiring, components),
                        self.raise_interrupt,
                    )
                )
            )

        await super().run_forever(state_consumer, state_producer)
        if self._tasks:
            await asyncio.wait(self._tasks)

    async def on_tick(self, time: SimTime, changes: Changes) -> None:
        """Delegates core behaviour to the slave scheduler.

        An asynchronous method which delegates core behaviour of computing changes and
        determining a callback period to the slave scheduler and sends the resulting
        Output.

        Args:
            time (SimTime): The current simulation time (in nanoseconds).
            changes (Changes): A mapping of changed component inputs and their new
                values.
        """
        on_tick = asyncio.create_task(self.scheduler.on_tick(time, changes))
        error_state = asyncio.create_task(self.scheduler.error.wait())

        done, _ = await asyncio.wait(
            [on_tick, error_state],
            return_when=asyncio.tasks.FIRST_COMPLETED,
        )
        if error_state in done:
            await self.state_producer.produce(
                output_topic(self.name),
                self.scheduler.component_error,
            )

        else:
            output_changes, call_in = on_tick.result()
            await self.output(time, output_changes, call_in)

    async def stop_component(self) -> None:
        """Cancel all pending tasks associated with the System Simulation component.

        Cancels long running adapter tasks associated with the component.
        """
        LOGGER.debug(f"Stopping {self.name}")
        for task in self._tasks:
            task.cancel()


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
