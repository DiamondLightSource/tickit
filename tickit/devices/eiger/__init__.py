from dataclasses import dataclass

from tickit.core.components.component import Component, ComponentConfig
from tickit.core.components.device_simulation import DeviceSimulation
from tickit.devices.eiger.eiger import EigerDevice
from tickit.devices.eiger.eiger_adapters import EigerRESTAdapter, EigerZMQAdapter


@dataclass
class Eiger(ComponentConfig):
    """Eiger simulation with HTTP adapter."""

    host: str = "0.0.0.0"
    port: int = 8081
    zmq_host: str = "127.0.0.1"
    zmq_port: int = 9999

    def __call__(self) -> Component:  # noqa: D102
        return DeviceSimulation(
            name=self.name,
            device=EigerDevice(),
            adapters=[
                EigerRESTAdapter(host=self.host, port=self.port),
                EigerZMQAdapter(zmq_host=self.zmq_host, zmq_port=self.zmq_port),
            ],
        )
