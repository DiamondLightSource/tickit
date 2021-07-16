from typing import Iterable, Set

from tickit.core.adapter import Adapter
from tickit.core.device import UpdateEvent
from tickit.core.typedefs import IoId, State
from tickit.utils.compat.functools_compat import cached_property


class Sink:
    @property
    def outputs(self) -> Set[IoId]:
        return set()

    @cached_property
    def adapters(self) -> Iterable[Adapter]:
        return list()

    def update(self, delta: int, inputs: State) -> UpdateEvent:
        print("Sunk {}".format(inputs))
        return UpdateEvent(State(dict()), None)
