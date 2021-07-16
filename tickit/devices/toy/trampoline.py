from random import randint
from typing import Dict, Iterable, Set

from tickit.core.adapter import Adapter
from tickit.core.device import UpdateEvent
from tickit.core.typedefs import IoId, SimTime, State
from tickit.utils.compat.functools_compat import cached_property


class Trampoline:
    def __init__(self, callback_period: int = int(1e9)) -> None:
        self.callback_period = SimTime(callback_period)

    @property
    def outputs(self) -> Set[IoId]:
        return set()

    @cached_property
    def adapters(self) -> Iterable[Adapter]:
        return list()

    def update(self, delta: int, inputs: State) -> UpdateEvent:
        print("Boing! ({}, {})".format(delta, inputs))
        return UpdateEvent(State(dict()), self.callback_period)


class RandomTrampoline:
    def __init__(self, callback_period: int = int(1e9)) -> None:
        self.callback_period = SimTime(callback_period)

    @property
    def outputs(self) -> Set[IoId]:
        return {IoId("output")}

    @property
    def adapters(self) -> Dict[str, Adapter]:
        return dict()

    def update(self, delta: int, inputs: State) -> UpdateEvent:
        output = randint(0, 255)
        print(
            "Boing! (delta: {}, inputs: {}, output: {})".format(delta, inputs, output)
        )
        return UpdateEvent(State({IoId("output"): output}), self.callback_period)
