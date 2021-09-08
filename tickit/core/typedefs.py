from dataclasses import dataclass
from typing import Hashable, NewType, Optional

from immutables import Map

ComponentID = NewType("ComponentID", str)
PortID = NewType("PortID", str)
State = NewType("State", Map[str, Hashable])
Changes = NewType("Changes", Map[str, Hashable])
SimTime = NewType("SimTime", int)


@dataclass(frozen=True)
class Input:
    target: ComponentID
    time: SimTime
    changes: Changes


@dataclass(frozen=True)
class Output:
    source: ComponentID
    time: SimTime
    changes: Changes
    call_in: Optional[SimTime]


@dataclass(frozen=True)
class Interrupt:
    source: ComponentID


@dataclass(frozen=True)
class Wakeup:
    component: ComponentID
    when: SimTime
