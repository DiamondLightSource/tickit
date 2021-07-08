from typing import Dict, Optional, Protocol, Tuple, runtime_checkable


@runtime_checkable
class Device(Protocol):
    @property
    def initial_state(self) -> Tuple[Dict[str, object], Optional[int]]:
        ...

    def update(
        self, delta: float, inputs: Dict[str, object]
    ) -> Tuple[Dict[str, object], Optional[int]]:
        ...
