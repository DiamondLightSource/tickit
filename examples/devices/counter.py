import logging
from dataclasses import dataclass

from tickit.core.components.component import Component, ComponentConfig
from tickit.core.components.device_simulation import DeviceSimulation
from tickit.core.device import Device, DeviceUpdate
from tickit.core.typedefs import SimTime
from tickit.utils.compat.typing_compat import TypedDict

LOGGER = logging.getLogger(__name__)


@dataclass
class Counter(ComponentConfig):
    """Simulation of simple counting device."""

    def __call__(self) -> Component:  # noqa: D102
        return DeviceSimulation(name=self.name, device=CounterDevice())


class CounterDevice(Device):
    """A simple device which increments a value."""

    #: An empty typed mapping of input values
    Inputs: TypedDict = TypedDict("Inputs", {})
    #: A typed mapping containing the 'value' output value
    Outputs: TypedDict = TypedDict("Outputs", {"value": int})

    def __init__(self, initial_value: int = 0, callback_period: int = int(1e9)) -> None:
        """A constructor of the counter, which increments the input value.

        Args:
            initial_value (Any): The initial value of the counter.
            callback_period (int): The simulation time callback period of the device
                (in nanoseconds). Defaults to int(1e9).
        """
        self._value = initial_value
        self.callback_period = SimTime(callback_period)
        LOGGER.debug(f"Counter initialized with value => {self._value}")

    def update(self, time: SimTime, inputs: Inputs) -> DeviceUpdate[Outputs]:
        """The update method which produces the incremented value.

        Args:
            time (SimTime): The current simulation time (in nanoseconds).
            inputs (State): A mapping of inputs to the device and their values.

        Returns:
            DeviceUpdate[Outputs]:
                The produced update event which contains the incremented value, and
                requests a callback after callback_period.
        """
        self._value = self._value + 1
        LOGGER.debug(f"Counter incremented to {self._value}")
        return DeviceUpdate(
            CounterDevice.Outputs(value=self._value),
            SimTime(time + self.callback_period),
        )
