import logging

from tickit.core.device import ConfigurableDevice, DeviceUpdate
from tickit.core.typedefs import SimTime
from tickit.utils.compat.typing_compat import TypedDict

LOGGER = logging.getLogger(__name__)


class Counter(ConfigurableDevice):
    """A simple device which increments a value."""

    #: An empty typed mapping of input values
    Inputs: TypedDict = TypedDict("Inputs", {})
    #: A typed mapping containing the 'value' output value
    Outputs: TypedDict = TypedDict("Outputs", {"value": int})

    def __init__(self, value: int = 0, callback_period: int = int(1e9)) -> None:
        """A constructor of the counter, which increments the input value.

        Args:
            value (Any): An incremented output value.
        """
        self.value = value
        self.callback_period = SimTime(callback_period)
        LOGGER.debug(f"Initialize with value => {self.value}")

    def update(self, time: SimTime, inputs: Inputs) -> DeviceUpdate[Outputs]:
        """The update method which produces the incremented value.

        Args:
            time (SimTime): The current simulation time (in nanoseconds).
            inputs (State): A mapping of inputs to the device and their values.

        Returns:
            DeviceUpdate[Outputs]:
                The produced update event which contains the incremented value, and
                never requests a callback.
        """
        self.value += 1
        LOGGER.debug("Incremented {}".format(self.value))
        return DeviceUpdate(
            Counter.Outputs(value=self.value), SimTime(time + self.callback_period)
        )
