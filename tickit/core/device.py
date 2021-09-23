from dataclasses import dataclass
from typing import Dict, Generic, Hashable, Mapping, Optional, Type, TypeVar

from tickit.core.typedefs import SimTime
from tickit.utils.compat.typing_compat import Protocol, runtime_checkable
from tickit.utils.configuration.configurable import configurable, configurable_base

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


@runtime_checkable
class Device(Protocol):
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
        pass


@configurable_base
@dataclass
class DeviceConfig:
    """A data container for device configuration.

    A data container for device configuration which acts as a named union of subclasses
    to facilitate automatic deserialization.
    """

    @staticmethod
    def configures() -> Type[Device]:
        """A static method which returns the Device class configured by this config.

        Returns:
            Type[Device]: The Device class configured by this config.
        """
        raise NotImplementedError

    @property
    def kwargs(self) -> Dict[str, object]:
        """A property which returns the key word arguments of the configured device.

        Returns:
            Dict[str, object]: The key word argument of the configured Device.
        """
        raise NotImplementedError


class ConfigurableDevice:
    """A mixin used to create a device with a configuration data container."""

    def __init_subclass__(cls) -> None:
        """A subclass init method which makes the subclass configurable.

        A subclass init method which makes the subclass configurable with a
        DeviceConfig template.
        """
        cls = configurable(DeviceConfig)(cls)
