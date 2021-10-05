from dataclasses import dataclass

from tickit.core.components.component import Component, ComponentConfig
from tickit.core.components.device_simulation import DeviceSimulation

from .cryostream import CryostreamAdapter, CryostreamDevice


@dataclass
class Cryostream(ComponentConfig):
    host: str = "localhost"
    port: int = 25565

    def __call__(self) -> Component:
        return DeviceSimulation(
            name=self.name,
            inputs=self.inputs,
            device=CryostreamDevice(),
            adapters=[CryostreamAdapter(host=self.host, port=self.port)],
        )
