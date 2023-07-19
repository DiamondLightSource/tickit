from dataclasses import dataclass
from typing import Dict, List

from tickit.adapters.composed import ComposedAdapter
from tickit.adapters.interpreters.command.command_interpreter import CommandInterpreter
from tickit.adapters.interpreters.command.regex_command import RegexCommand
from tickit.adapters.servers.tcp import TcpServer
from tickit.core.components.component import Component, ComponentConfig
from tickit.core.components.device_simulation import DeviceSimulation
from tickit.core.components.system_simulation import SystemSimulationComponent
from tickit.core.components.system_simulation_view import SystemSimulationView
from tickit.core.typedefs import ComponentID, ComponentPort, PortID
from tickit.utils.byte_format import ByteFormat


class SystemSimulationAdapter(ComposedAdapter[bytes, SystemSimulationView]):
    """Network adapter for a generic system simulation.

    Can be used to query the system simulation component for a list of the
    ComponentID's for the components in the system and given a specific ID, the details
    of that component.
    """

    device: SystemSimulationView

    @RegexCommand(r"ids", False, "utf-8")
    async def get_cpt_ids(self) -> bytes:
        """Returns a list of ids for all the components in the system simulation."""
        return str(self.device.get_component_ids()).encode("utf-8")

    @RegexCommand(r"id=(\w+)", False, "utf-8")
    async def get_cpt_info(self, id: str) -> bytes:
        """Returns the component info of the given id."""
        component = self.device._components.get(
            ComponentID(id), "ComponentID not recognised."
        )
        if isinstance(component, DeviceSimulation):
            return str(
                f"ComponentID: {component.name}\n"
                + f" device: {component.device.__class__.__name__}\n"
                + " adapters: "
                + f"{[adapter.__class__.__name__ for adapter in component.adapters]}\n"
                + f" Inputs: {component.device_inputs}\n"
                + f" last_outputs: {component.last_outputs}\n"
            ).encode("utf-8")
        else:
            return str(component).encode("utf-8")

    @RegexCommand(r"wiring", False, "utf-8")
    async def get_wiring(self) -> bytes:
        """Returns the wiring object used by the nested scheduler."""
        return str(self.device.get_wiring()).encode("utf-8")


@dataclass
class SystemSimulationWithAdapter(ComponentConfig):
    """Simulation of a nested set of components with a composed adapter."""

    name: ComponentID
    inputs: Dict[PortID, ComponentPort]
    components: List[ComponentConfig]
    expose: Dict[PortID, ComponentPort]

    def __call__(self) -> Component:  # noqa: D102
        return SystemSimulationComponent(
            name=self.name,
            components=self.components,
            expose=self.expose,
            adapter=SystemSimulationAdapter(
                TcpServer(host="localhost", port=25560, format=ByteFormat(b"%b\r\n")),
                CommandInterpreter(),
            ),
        )
