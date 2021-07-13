from functools import cached_property
from typing import Dict, Iterable, Optional, Protocol, Tuple, runtime_checkable

from tickit.core.adapter import Adapter


@runtime_checkable
class Device(Protocol):
    @property
    def initial_state(self) -> Tuple[Dict[str, object], Optional[int]]:
        ...

    @cached_property
    def adapters(self) -> Iterable[Adapter]:
        ...

    def update(
        self, delta: float, inputs: Dict[str, object]
    ) -> Tuple[Dict[str, object], Optional[int]]:
        ...
