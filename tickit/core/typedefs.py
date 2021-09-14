from dataclasses import dataclass
from typing import Hashable, Mapping, NewType, Optional

from apischema import deserializer, serializer
from immutables import Map

#: An identifier which specifies the component
ComponentID = NewType("ComponentID", str)
#: An identifier which specifies the input/output port of a component
PortID = NewType("PortID", str)
#: A mapping of PortID to component input/output property
State = NewType("State", Mapping[PortID, Hashable])
#: A mapping of the difference between State mappings
Changes = NewType("Changes", Map[PortID, Hashable])
#: Simulation Time in nanoseconds
SimTime = NewType("SimTime", int)


@dataclass(frozen=True)
class ComponentPort:
    """An immutable dataclass for custom (de)serialization of component - port pairs"""

    component: ComponentID
    port: PortID

    def __repr__(self) -> str:
        return ":".join((self.component, self.port))

    @serializer
    def serialize(self) -> str:
        """An apischema serialization method which returns a string of component:port

        Returns:
            str: The serialized ComponentPort, in format component:port
        """
        return str(self)

    @deserializer
    @staticmethod
    def deserialize(data: str) -> "ComponentPort":
        """An apischema deserialization method which builds a from a string of component:port

        Returns:
            ComponentPort: The deserialized ComponentPort
        """
        component, port = data.split(":")
        return ComponentPort(ComponentID(component), PortID(port))

    def __iter__(self):
        return (x for x in (self.component, self.port))


@dataclass(frozen=True)
class Input:
    """An immutable data container for Component inputs

    Args:
        target: The Component which is to handle the Input
        time: The simulation time at which the Input was produced and is to be handled
        changes: The changes to the component inputs
    """

    target: ComponentID
    time: SimTime
    changes: Changes


@dataclass(frozen=True)
class Output:
    """An immutable data container for Component outputs

    Args:
        source: The Component which produced the Output
        time: The simulation time at which the Output was produced and is to be handled
        changes: The changes to the component outputs
        call_in: The duration after which the component requests to be awoken
    """

    source: ComponentID
    time: SimTime
    changes: Changes
    call_in: Optional[SimTime]


@dataclass(frozen=True)
class Interrupt:
    """An immutable data container for scheduling Component interrupts

    Args:
        component: The Component which is requesting an interrupt
    """

    source: ComponentID


@dataclass(frozen=True)
class Wakeup:
    """An immutable data container for scheduling Component wakeups

    Args:
        component: The Component which should be awoken
        when: The simulation time at which the component should be awoken
    """

    component: ComponentID
    when: SimTime
