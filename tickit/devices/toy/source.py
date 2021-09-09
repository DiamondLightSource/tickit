from typing import Any

from immutables import Map

from tickit.core.device import ConfigurableDevice, UpdateEvent
from tickit.core.typedefs import SimTime, State


class Source(ConfigurableDevice):
    def __init__(self, value: Any) -> None:
        self.value = value

    def update(self, time: SimTime, inputs: State) -> UpdateEvent:
        print("Sourced {}".format(self.value))
        return UpdateEvent(State(Map({"value": self.value})), None)
