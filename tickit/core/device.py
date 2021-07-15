from dataclasses import dataclass
from typing import Dict, Iterable, Optional, Set

from tickit.core.adapter import Adapter
from tickit.core.typedefs import IoId
from tickit.utils.compat.functools import cached_property
from tickit.utils.compat.typing import Protocol, runtime_checkable


@dataclass
class UpdateEvent:
    state: Dict[str, object]
    call_in: Optional[int]


@runtime_checkable
class Device(Protocol):
    @property
    def outputs(self) -> Set[IoId]:
        ...

    @cached_property
    def adapters(self) -> Iterable[Adapter]:
        ...

    def update(self, delta: int, inputs: Dict[str, object]) -> UpdateEvent:
        ...
