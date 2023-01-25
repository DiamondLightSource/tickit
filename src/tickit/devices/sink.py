import logging
from typing import Any

from tickit.core.components.component import Component, ComponentConfig
from tickit.core.components.device_simulation import DeviceSimulation
from tickit.core.device import Device, DeviceUpdate
from tickit.core.typedefs import SimTime
from tickit.utils.compat.typing_compat import TypedDict

LOGGER = logging.getLogger(__name__)


class SinkDevice(Device):
    """A simple device which can take any input and produces no output."""

    #: A typed mapping containing the 'input' input value
    Inputs: TypedDict = TypedDict("Inputs", {"input": Any})
    #: An empty typed mapping of device outputs
    Outputs: TypedDict = TypedDict("Outputs", {})

    def update(self, time: SimTime, inputs: Inputs) -> DeviceUpdate[Outputs]:
        """The update method which logs the inputs at debug level and produces no outputs.

        Args:
            time (SimTime): The current simulation time (in nanoseconds).
            inputs (State): A mapping of inputs to the device and their values.

        Returns:
            DeviceUpdate[Outputs]:
                The produced update event which never contains any changes, and never
                requests a callback.
        """
        LOGGER.debug("Sunk {}".format({k: v for k, v in inputs.items()}))
        return DeviceUpdate(SinkDevice.Outputs(), None)


class Sink(ComponentConfig):
    """Arbitrary value sink that logs the value."""

    def __call__(self) -> Component:  # noqa: D102
        return DeviceSimulation(
            name=self.name,
            device=SinkDevice(),
        )
