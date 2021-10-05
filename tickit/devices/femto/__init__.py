from dataclasses import dataclass

from tickit.core.components.component import Component, ComponentConfig
from tickit.core.components.device_simulation import DeviceSimulation

from .femto import CurrentDevice, FemtoAdapter, FemtoDevice


@dataclass
class Femto(ComponentConfig):
    initial_gain: float = 2.5
    initial_current: float = 0.0
    db_file: str = "tickit/devices/femto/record.db"
    ioc_name: str = "FEMTO"

    def __call__(self) -> Component:
        return DeviceSimulation(
            name=self.name,
            inputs=self.inputs,
            device=FemtoDevice(
                initial_gain=self.initial_gain, initial_current=self.initial_current
            ),
            adapters=[FemtoAdapter(db_file=self.db_file, ioc_name=self.ioc_name)],
        )


@dataclass
class Current(ComponentConfig):
    callback_period: int = int(1e9)

    def __call__(self) -> Component:
        return DeviceSimulation(
            name=self.name,
            inputs=self.inputs,
            device=CurrentDevice(callback_period=self.callback_period),
        )
