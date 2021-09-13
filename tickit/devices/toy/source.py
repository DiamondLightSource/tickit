import logging
from typing import Any

from tickit.core.device import ConfigurableDevice, DeviceUpdate
from tickit.core.typedefs import SimTime
from tickit.utils.compat.typing_compat import TypedDict

LOGGER = logging.getLogger(__name__)


class Source(ConfigurableDevice):
    Inputs: TypedDict = TypedDict("Inputs", {})
    Outputs: TypedDict = TypedDict("Outputs", {"value": Any})

    def __init__(self, value: Any) -> None:
        self.value = value

    def update(
        self, time: SimTime, inputs: "Source.Inputs"
    ) -> DeviceUpdate["Source.Outputs"]:
        LOGGER.debug("Sourced {}".format(self.value))
        return DeviceUpdate(Source.Outputs(value=self.value), None)
