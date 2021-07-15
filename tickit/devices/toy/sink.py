from typing import Dict, Iterable, Optional, Set, Tuple

from tickit.core.adapter import Adapter
from tickit.core.typedefs import IoId
from tickit.utils.compat.functools import cached_property


class Sink:
    @property
    def outputs(self) -> Set[IoId]:
        return set()

    @cached_property
    def adapters(self) -> Iterable[Adapter]:
        return list()

    def update(
        self, delta: int, inputs: Dict[str, object]
    ) -> Tuple[Dict[str, object], Optional[int]]:
        print("Sunk {}".format(inputs))
        return (dict(), None)
