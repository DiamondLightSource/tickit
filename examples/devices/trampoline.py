import logging
from dataclasses import dataclass
from random import randint

from tickit.core.components.component import Component, ComponentConfig
from tickit.core.components.device_simulation import DeviceSimulation
from tickit.core.device import Device, DeviceUpdate
from tickit.core.typedefs import SimTime
from tickit.utils.compat.typing_compat import TypedDict

LOGGER = logging.getLogger(__name__)


class TrampolineDevice(Device):
    """A trivial toy device which requests a callback every update."""

    #: An empty typed mapping of device inputs
    Inputs: TypedDict = TypedDict("Inputs", {})
    #: An empty typed mapping of device outputs
    Outputs: TypedDict = TypedDict("Outputs", {})

    def __init__(self, callback_period: int = int(1e9)) -> None:
        """A constructor of the sink which configures the device callback period.

        Args:
            callback_period (int): The simulation time callback period of the device
                (in nanoseconds). Defaults to int(1e9).
        """
        self.callback_period = SimTime(callback_period)

    def update(self, time: SimTime, inputs: Inputs) -> DeviceUpdate[Outputs]:
        """The update method which prints the inputs and requests a callback.

        The update method which prints the time of the update and the inputs then
        returns an empty output mapping and a request to be called back after the
        configured callback period.

        Args:
            time (SimTime): The current simulation time (in nanoseconds).
            inputs (State): A mapping of inputs to the device and their values.

        Returns:
            DeviceUpdate[Outputs]:
                The produced update event which never contains any changes, and
                requests a callback after the configured callback period.
        """
        LOGGER.debug(f"Boing! ({time}, {inputs})")
        return DeviceUpdate(
            TrampolineDevice.Outputs(), SimTime(time + self.callback_period)
        )


class RandomTrampolineDevice(Device):
    """A trivial toy device which produced a random output and requests a callback."""

    #: An empty typed mapping of device inputs
    Inputs: TypedDict = TypedDict("Inputs", {})
    #: A typed mapping containing the 'output' output value
    Outputs: TypedDict = TypedDict("Outputs", {"output": int})

    def __init__(self, callback_period: int = int(1e9)) -> None:
        """A constructor of the sink which configures the device callback period.

        Args:
            callback_period (int): The simulation time callback period of the device
                (in nanoseconds). Defaults to int(1e9).
        """
        self.callback_period = SimTime(callback_period)

    def update(self, time: SimTime, inputs: Inputs) -> DeviceUpdate[Outputs]:
        """The update method which produces a random output and requests a callback.

        The update method which prints the time of the update, the inputs and the
        output which will be produced then returns the random output value and a
        request to be called back after the configured callback period.

        Args:
            time (SimTime): The current simulation time (in nanoseconds).
            inputs (State): A mapping of inputs to the device and their values.

        Returns:
            DeviceUpdate[Outputs]:
                The produced update event which contains the value of the random output,
                and requests a callback after the configured callback period.
        """
        output = randint(0, 255)
        LOGGER.debug(f"Boing! (delta: {time}, inputs: {inputs}, output: {output})")
        return DeviceUpdate(
            RandomTrampolineDevice.Outputs(output=output),
            SimTime(time + self.callback_period),
        )


@dataclass
class RandomTrampoline(ComponentConfig):
    """Random thing that goes boing."""

    callback_period: int = int(1e9)

    def __call__(self) -> Component:  # noqa: D102
        return DeviceSimulation(
            name=self.name,
            device=RandomTrampolineDevice(callback_period=self.callback_period),
        )
