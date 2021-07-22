from dataclasses import dataclass
from typing import Set

from tickit.core.device import DeviceConfig, UpdateEvent
from tickit.core.typedefs import IoId, SimTime, State


@dataclass
class SinkConfig(DeviceConfig):
    device_class = "tickit.devices.toy.sink.Sink"


class Sink:
    def __init__(self, config: SinkConfig) -> None:
        ...

    @property
    def outputs(self) -> Set[IoId]:
        return set()

    def update(self, time: SimTime, inputs: State) -> UpdateEvent:
        print("Sunk {}".format(inputs))
        return UpdateEvent(State(dict()), None)
