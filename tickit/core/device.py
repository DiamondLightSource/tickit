from dataclasses import dataclass
from typing import Optional, Set

from tickit.core.typedefs import IoId, SimTime, State
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

    def update(self, time: SimTime, inputs: State) -> UpdateEvent:
        ...
