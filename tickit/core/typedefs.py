from dataclasses import dataclass
from typing import Hashable, Mapping, NewType, Optional

from apischema import deserializer, serializer
from immutables import Map

ComponentID = NewType("ComponentID", str)
PortID = NewType("PortID", str)
State = NewType("State", Mapping[PortID, Hashable])
Changes = NewType("Changes", Map[PortID, Hashable])
SimTime = NewType("SimTime", int)


@dataclass(frozen=True)
class ComponentPort:
    component: ComponentID
    port: PortID

    def __repr__(self) -> str:
        return ":".join((self.component, self.port))

    @serializer
    def serialize(self) -> str:
        return str(self)

    @deserializer
    @staticmethod
    def deserialize(data: str) -> "ComponentPort":
        component, port = data.split(":")
        return ComponentPort(ComponentID(component), PortID(port))

    def __iter__(self):
        return (x for x in (self.component, self.port))


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
