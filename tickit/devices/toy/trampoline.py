from random import randint
from typing import Dict, Iterable, Optional, Set, Tuple

from tickit.core.adapter import Adapter
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

    def update(
        self, delta: int, inputs: Dict[str, object]
    ) -> Tuple[Dict[str, object], Optional[int]]:
        print("Boing! ({}, {})".format(delta, inputs))
        return (dict(), self.callback_period)


class RandomTrampoline:
    def __init__(self, callback_period: int = 1e9) -> None:
        self.callback_period = callback_period

    @property
    def outputs(self) -> Set[IoId]:
        return {"output"}

    @property
    def adapters(self) -> Dict[str, Adapter]:
        return dict()

    def update(
        self, delta: int, inputs: Dict[str, object]
    ) -> Tuple[Dict[str, object], Optional[int]]:
        output = randint(0, 255)
        print(
            "Boing! (delta: {}, inputs: {}, output: {})".format(delta, inputs, output)
        )
        return ({"output": output}, self.callback_period)
