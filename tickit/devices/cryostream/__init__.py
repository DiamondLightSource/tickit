from dataclasses import dataclass

from tickit.core.components.component import Component, ComponentConfig
from tickit.core.components.device_simulation import DeviceSimulation

from .cryostream import CryostreamAdapter, CryostreamDevice


@dataclass
class Cryostream(ComponentConfig):
    """Cryostream simulation with TCP server."""

    host: str = "localhost"
    port: int = 25565

    def __call__(self) -> Component:  # noqa: D102
        return DeviceSimulation(
            name=self.name,
            device=CryostreamDevice(),
            adapters=[CryostreamAdapter(host=self.host, port=self.port)],
        )
