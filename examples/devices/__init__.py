from dataclasses import dataclass

from tickit.core.components.component import Component, ComponentConfig
from tickit.core.components.device_simulation import DeviceSimulation

from .counter import CounterDevice


@dataclass
class Counter(ComponentConfig):
    """Simulation of simple counting device."""

    def __call__(self) -> Component:  # noqa: D102
        return DeviceSimulation(name=self.name, device=CounterDevice())
