from immutables import Map

from tickit.core.device import ConfigurableDevice, UpdateEvent
from tickit.core.typedefs import SimTime, State


class Sink(ConfigurableDevice):
    def __init__(self) -> None:
        pass

    def update(self, time: SimTime, inputs: State) -> UpdateEvent:
        print("Sunk {}".format({k: v for k, v in inputs.items()}))
        return UpdateEvent(State(Map()), None)
