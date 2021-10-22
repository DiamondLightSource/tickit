from dataclasses import dataclass

from tickit.core.components.component import Component, ComponentConfig
from tickit.core.components.device_simulation import DeviceSimulation

from .eiger import EigerAdapter, EigerDevice


@dataclass
class Eiger(ComponentConfig):
    """Eiger simulation with HTTP adapter."""

    host: str = "0.0.0.0"
    port: int = 8081

    def __call__(self) -> Component:  # noqa: D102
        return DeviceSimulation(
            name=self.name,
            device=EigerDevice(),
            adapters=[EigerAdapter(host=self.host, port=self.port)],
        )
