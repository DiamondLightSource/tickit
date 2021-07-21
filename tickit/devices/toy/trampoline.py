from random import randint
from typing import Set

from tickit.core.device import UpdateEvent
from tickit.core.typedefs import IoId, SimTime, State


class Trampoline:
    def __init__(self, callback_period: int = int(1e9)) -> None:
        self.callback_period = SimTime(callback_period)

    @property
    def outputs(self) -> Set[IoId]:
        return set()

    def update(self, time: SimTime, inputs: State) -> UpdateEvent:
        print("Boing! ({}, {})".format(time, inputs))
        return UpdateEvent(State(dict()), self.callback_period)


class RandomTrampoline:
    def __init__(self, callback_period: int = int(1e9)) -> None:
        self.callback_period = SimTime(callback_period)

    @property
    def outputs(self) -> Set[IoId]:
        return {IoId("output")}

    def update(self, time: SimTime, inputs: State) -> UpdateEvent:
        output = randint(0, 255)
        print("Boing! (delta: {}, inputs: {}, output: {})".format(time, inputs, output))
        return UpdateEvent(State({IoId("output"): output}), self.callback_period)
