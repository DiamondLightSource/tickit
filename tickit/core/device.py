from dataclasses import dataclass
from typing import Iterable, Optional, Set

from tickit.core.adapter import Adapter
from tickit.core.typedefs import IoId, SimTime, State
from tickit.utils.compat.functools_compat import cached_property
from tickit.utils.compat.typing_compat import Protocol, runtime_checkable


@dataclass
class UpdateEvent:
    state: State
    call_in: Optional[SimTime]


@runtime_checkable
class Device(Protocol):
    @property
    def outputs(self) -> Set[IoId]:
        ...

    @cached_property
    def adapters(self) -> Iterable[Adapter]:
        ...

    def update(self, delta: SimTime, inputs: State) -> UpdateEvent:
        ...
