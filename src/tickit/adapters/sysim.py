from typing import Dict, List

import pydantic.v1.dataclasses

from tickit.adapters.io.tcp_io import TcpIo
from tickit.adapters.system_adapter import SystemSimulationAdapter
from tickit.core.adapter import AdapterContainer
from tickit.core.components.component import Component, ComponentConfig
from tickit.core.components.system_simulation import SystemSimulationComponent
from tickit.core.typedefs import ComponentID, ComponentPort, PortID


@pydantic.v1.dataclasses.dataclass
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
            adapter=AdapterContainer(
                SystemSimulationAdapter(),
                TcpIo(host="localhost", port=25560),
            ),
        )
