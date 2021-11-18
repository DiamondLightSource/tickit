from dataclasses import dataclass
from typing import Generic, Hashable, Mapping, Optional, TypeVar

from tickit.core.typedefs import SimTime
from tickit.utils.configuration.configurable import as_tagged_union

#: A bound typevar for mappings of device inputs
InMap = TypeVar("InMap", bound=Mapping[str, Hashable])
#: A bound typevar for mappings of device outputs
OutMap = TypeVar("OutMap", bound=Mapping[str, Hashable])


@dataclass
class DeviceUpdate(Generic[OutMap]):
    """An immutable data container for Device outputs and callback request time.

    Args:
        outputs: A mapping of device output keys and current values.
        call_at: The simulation time at which the component requests to be awoken.
    """

    outputs: OutMap
    call_at: Optional[SimTime]


@as_tagged_union
class Device(Generic[InMap, OutMap]):
    """An interface for types which implement simulated devices."""

    def update(self, time: SimTime, inputs: InMap) -> DeviceUpdate[OutMap]:
        """A method which implements device behaviour according to the time and its inputs.

        A method which implements the (typically physics based) changes which occur
        within the device in response to either the progression of time or the
        alteration of inputs to the device. The method returns the new observable state
        of the device and may optionally include a time in which the method should be
        called again.

        Args:
            time: The current simulation time (in nanoseconds).
            inputs: A mapping of device inputs and their values.
        """
