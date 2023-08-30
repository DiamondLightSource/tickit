from dataclasses import dataclass
from typing import Hashable, Iterator, Mapping, NewType, Optional, Union

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
    """An immutable dataclass for custom (de)serialization of component - port pairs."""

    component: ComponentID
    port: PortID

    def __repr__(self) -> str:
        """A string representation of the object of format component:port.

        Returns:
            str: A string representation of the object of format component:port.
        """
        return ":".join((self.component, self.port))

    def __iter__(self) -> Iterator:
        """An iterator which returns (component, port).

        Returns:
            Iterator: An iterator containing (component, port).
        """
        return (x for x in (self.component, self.port))


@dataclass(frozen=True)
class Input:
    """An immutable data container for Component inputs.

    Args:
        target: The Component which is to handle the Input.
        time: The simulation time at which the Input was produced and is to be handled.
        changes: The changes to the component inputs.
    """

    target: ComponentID
    time: SimTime
    changes: Changes


@dataclass(frozen=True, init=True)
class StopComponent:
    """An immutable dataclass to register Component shutdown."""

    ...


@dataclass(frozen=True)
class Output:
    """An immutable data container for Component outputs.

    Args:
        source: The Component which produced the Output.
        time: The simulation time at which the Output was produced and is to be handled.
        changes: The changes to the component outputs.
        call_in: The duration after which the component requests to be awoken.
    """

    source: ComponentID
    time: SimTime
    changes: Changes
    call_at: Optional[SimTime]


@dataclass(frozen=True)
class Skip:
    """An immutable data container for skipping Component Updates.

    This mimics a Component output but is produced and consumed by the scheduler for
    situations where a components inputs has not changed, therefore does not need
    updating but this skipping needs to propgate through the graph.

    Args:
        source: The Component whos update will be skipped
        time: The simulation time at which the component skipping is to be handled.
        changes: The changes to the component outputs, which will always be an empty
            map.
    """

    source: ComponentID
    time: SimTime
    changes: Changes


@dataclass(frozen=True)
class Interrupt:
    """An immutable data container for scheduling Component interrupts.

    Args:
        component: The Component which is requesting an interrupt.
    """

    source: ComponentID


@dataclass(frozen=True)
class ComponentException:
    """An immutable data container for raising Component exceptions.

    Args:
        component: The Component which raised an exception.
    """

    source: ComponentID
    error: Exception
    traceback: str


ComponentOutput = Union[Interrupt, Output, ComponentException]
ComponentInput = Union[Input, StopComponent, ComponentException]
