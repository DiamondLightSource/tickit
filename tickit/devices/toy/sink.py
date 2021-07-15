from typing import Dict, Iterable, Set

from tickit.core.adapter import Adapter
from tickit.core.device import UpdateEvent
from tickit.core.typedefs import IoId
from tickit.utils.compat.functools import cached_property


class Sink:
    @property
    def outputs(self) -> Set[IoId]:
        return set()

    @cached_property
    def adapters(self) -> Iterable[Adapter]:
        return list()

    def update(self, delta: int, inputs: Dict[str, object]) -> UpdateEvent:
        print("Sunk {}".format(inputs))
        return UpdateEvent(dict(), None)
