from random import randint
from typing import Dict, Iterable, Set

from tickit.core.adapter import Adapter
from tickit.core.device import UpdateEvent
from tickit.core.typedefs import IoId
from tickit.utils.compat.functools import cached_property


class Trampoline:
    def __init__(self, callback_period: int = 1e9) -> None:
        self.callback_period = callback_period

    @property
    def outputs(self) -> Set[IoId]:
        return set()

    @cached_property
    def adapters(self) -> Iterable[Adapter]:
        return list()

    def update(self, delta: int, inputs: Dict[str, object]) -> UpdateEvent:
        print("Boing! ({}, {})".format(delta, inputs))
        return UpdateEvent(dict(), self.callback_period)


class RandomTrampoline:
    def __init__(self, callback_period: int = 1e9) -> None:
        self.callback_period = callback_period

    @property
    def outputs(self) -> Set[IoId]:
        return {"output"}

    @property
    def adapters(self) -> Dict[str, Adapter]:
        return dict()

    def update(self, delta: int, inputs: Dict[str, object]) -> UpdateEvent:
        output = randint(0, 255)
        print(
            "Boing! (delta: {}, inputs: {}, output: {})".format(delta, inputs, output)
        )
        return UpdateEvent({"output": output}, self.callback_period)
