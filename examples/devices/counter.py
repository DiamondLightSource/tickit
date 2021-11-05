import logging

from tickit.adapters.zmqadapter import ZeroMQAdapter
from tickit.core.device import Device, DeviceUpdate
from tickit.core.typedefs import SimTime
from tickit.utils.compat.typing_compat import TypedDict

LOGGER = logging.getLogger(__name__)


class CounterDevice(Device):
    """A simple device which increments a value."""

    #: An empty typed mapping of input values
    Inputs: TypedDict = TypedDict("Inputs", {})
    #: A typed mapping containing the 'value' output value
    Outputs: TypedDict = TypedDict("Outputs", {"value": int})

    def __init__(self, initial_value: int = 0, callback_period: int = int(1e9)) -> None:
        """A constructor of the counter, which increments the input value.

        Args:
            initial_value (Any): A value to increment.
            callback_period (int): The simulation time callback period of the device
                (in nanoseconds). Defaults to int(1e9).
        """
        self._value = initial_value
        self.callback_period = SimTime(callback_period)
        LOGGER.debug(f"Initialize with value => {self._value}")

    def update(self, time: SimTime, inputs: Inputs) -> DeviceUpdate[Outputs]:
        """The update method which produces the incremented value.

        Args:
            time (SimTime): The current simulation time (in nanoseconds).
            inputs (State): A mapping of inputs to the device and their values.

        Returns:
            DeviceUpdate[Outputs]:
                The produced update event which contains the incremented value, and
                requests a callback of 1s.
        """
        self._value = self._value + 1
        LOGGER.debug("Incremented to {}".format(self._value))
        return DeviceUpdate(
            CounterDevice.Outputs(value=self._value),
            SimTime(time + self.callback_period),
        )


class CounterAdapter(ZeroMQAdapter):
    """An adapter for the Counter's data stream."""

    device: CounterDevice

    def after_update(self) -> None:
        """Updates IOC values immediately following a device update."""
        current_value = self.device._value
        LOGGER.debug(f"Value updated to : {current_value}")
        self.send_message(current_value)
