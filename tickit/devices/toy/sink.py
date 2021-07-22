from dataclasses import dataclass

from tickit.core.device import DeviceConfig, UpdateEvent
from tickit.core.typedefs import SimTime, State


@dataclass
class SinkConfig(DeviceConfig):
    device_class = "tickit.devices.toy.sink.Sink"


class Sink:
    def update(self, time: SimTime, inputs: State) -> UpdateEvent:
        print("Sunk {}".format(inputs))
        return UpdateEvent(State(dict()), None)
