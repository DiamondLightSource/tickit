from dataclasses import dataclass

from tickit.core.components.component import Component, ComponentConfig
from tickit.core.components.device_simulation import DeviceSimulation

from .pneumatic import PneumaticAdapter, PneumaticDevice


@dataclass
class Pneumatic(ComponentConfig):
    initial_speed: float = 2.5
    initial_state: bool = False
    db_file: str = "tickit/devices/pneumatic/db_files/filter1.db"
    ioc_name: str = "PNEUMATIC"

    def __call__(self) -> Component:
        return DeviceSimulation(
            name=self.name,
            inputs=self.inputs,
            device=PneumaticDevice(
                initial_speed=self.initial_speed, initial_state=self.initial_state
            ),
            adapters=[PneumaticAdapter(db_file=self.db_file, ioc_name=self.ioc_name)],
        )
