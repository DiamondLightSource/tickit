from dataclasses import dataclass
from typing import Type

from tickit.core.components.component import BaseComponent, ComponentConfig
from tickit.core.components.device_simulation import DeviceSimulation
from tickit.core.state_interfaces.state_interface import StateConsumer, StateProducer

from .cryostream import CryostreamAdapter, CryostreamDevice


@dataclass
class Cryostream(ComponentConfig):
    host: str = "localhost"
    port: int = 25565

    def __call__(
        self, state_consumer: Type[StateConsumer], state_producer: Type[StateProducer]
    ) -> BaseComponent:
        device = CryostreamDevice()
        return DeviceSimulation(
            name=self.name,
            state_consumer=state_consumer,
            state_producer=state_producer,
            adapters=[CryostreamAdapter(host=self.host, port=self.port)],
            device=device,
        )
