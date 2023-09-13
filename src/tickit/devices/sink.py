import logging
from typing import Any, TypedDict

import pydantic.v1.dataclasses

from tickit.core.components.component import Component, ComponentConfig
from tickit.core.components.device_component import DeviceComponent
from tickit.core.device import Device, DeviceUpdate
from tickit.core.typedefs import SimTime

LOGGER = logging.getLogger(__name__)


class SinkDevice(Device):
    """A simple device which can take any input and produces no output."""

    #: A typed mapping containing the 'input' input value
    class Inputs(TypedDict):
        input: Any

    #: An empty typed mapping of device outputs
    class Outputs(TypedDict):
        ...

    def update(self, time: SimTime, inputs: Inputs) -> DeviceUpdate[Outputs]:
        """The update method which logs the inputs and produces no outputs.

        Args:
            time (SimTime): The current simulation time (in nanoseconds).
            inputs (State): A mapping of inputs to the device and their values.

        Returns:
            DeviceUpdate[Outputs]:
                The produced update event which never contains any changes, and never
                requests a callback.
        """
        LOGGER.debug(f"Sunk { {k: v for k, v in inputs.items()} }")
        return DeviceUpdate(SinkDevice.Outputs(), None)


@pydantic.v1.dataclasses.dataclass
class Sink(ComponentConfig):
    """Arbitrary value sink that logs the value."""

    def __call__(self) -> Component:  # noqa: D102
        return DeviceComponent(
            name=self.name,
            device=SinkDevice(),
        )
