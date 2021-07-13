from typing import Dict, Iterable, Optional, Tuple

from tickit.core.adapter import Adapter


class Sink:
    @property
    def initial_state(self) -> Tuple[Dict[str, object], Optional[int]]:
        return (dict(), None)

    @property
    def adapters(self) -> Iterable[Adapter]:
        return list()

    def update(
        self, delta: int, inputs: Dict[str, object]
    ) -> Tuple[Dict[str, object], Optional[int]]:
        print("Sunk {}".format(inputs))
        return (dict(), None)
