from tickit.core.device import ConfigurableDevice, UpdateEvent
from tickit.core.typedefs import SimTime, State


class Sink(ConfigurableDevice):
    def __init__(self) -> None:
        pass

    def update(self, time: SimTime, inputs: State) -> UpdateEvent:
        print("Sunk {}".format(inputs))
        return UpdateEvent(State(dict()), None)
