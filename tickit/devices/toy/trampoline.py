from random import randint

from tickit.core.device import ConfigurableDevice, UpdateEvent
from tickit.core.typedefs import SimTime, State
from tickit.utils.compat.typing_compat import TypedDict


class Trampoline(ConfigurableDevice):
    def __init__(self, callback_period: int = int(1e9)) -> None:
        self.callback_period = SimTime(callback_period)

    def update(self, time: SimTime, inputs: State) -> UpdateEvent:
        print("Boing! ({}, {})".format(time, inputs))
        return UpdateEvent(State(dict()), self.callback_period)


class RandomTrampoline(ConfigurableDevice):
    Output = TypedDict("Output", {"output": int})

    def __init__(self, callback_period: int = int(1e9)) -> None:
        self.callback_period = SimTime(callback_period)

    def update(self, time: SimTime, inputs: State) -> UpdateEvent:
        output = randint(0, 255)
        print("Boing! (delta: {}, inputs: {}, output: {})".format(time, inputs, output))
        return UpdateEvent(RandomTrampoline.Output(output=output), self.callback_period)
