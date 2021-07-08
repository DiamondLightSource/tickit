from typing import Dict, Optional, Tuple


class Sink:
    @property
    def initial_state(self) -> Tuple[Dict[str, object], Optional[int]]:
        return (dict(), None)

    def update(
        self, delta: int, inputs: Dict[str, object]
    ) -> Tuple[Dict[str, object], Optional[int]]:
        print("Sunk {}".format(inputs))
        return (dict(), None)
