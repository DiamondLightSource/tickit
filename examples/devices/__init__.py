from dataclasses import dataclass

from tickit.core.components.component import Component, ComponentConfig
from tickit.core.components.device_simulation import DeviceSimulation

from .counter import CounterAdapter, CounterDevice


@dataclass
class Counter(ComponentConfig):
    """Eiger simulation with HTTP adapter."""

    host: str = "127.0.0.1"
    port: int = 5555

    def __call__(self) -> Component:  # noqa: D102
        return DeviceSimulation(
            name=self.name,
            device=CounterDevice(),
            adapters=[CounterAdapter(zmq_host=self.host, zmq_port=self.port)],
        )
