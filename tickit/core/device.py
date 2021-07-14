from functools import cached_property
from typing import Dict, Iterable, Optional, Protocol, Set, Tuple, runtime_checkable

from tickit.core.adapter import Adapter
from tickit.core.typedefs import IoId


@runtime_checkable
class Device(Protocol):
    @property
    def outputs(self) -> Set[IoId]:
        ...

    @cached_property
    def adapters(self) -> Iterable[Adapter]:
        ...

    def update(
        self, delta: float, inputs: Dict[str, object]
    ) -> Tuple[Dict[str, object], Optional[int]]:
        ...
