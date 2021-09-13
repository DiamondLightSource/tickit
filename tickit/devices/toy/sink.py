from typing import Any

from tickit.core.device import ConfigurableDevice, DeviceUpdate
from tickit.core.typedefs import SimTime
from tickit.utils.compat.typing_compat import TypedDict


class Sink(ConfigurableDevice):
    Inputs: TypedDict = TypedDict("Inputs", {"input": Any})
    Outputs: TypedDict = TypedDict("Outputs", {})

    def __init__(self) -> None:
        pass

    def update(
        self, time: SimTime, inputs: "Sink.Inputs"
    ) -> DeviceUpdate["Sink.Outputs"]:
        print("Sunk {}".format({k: v for k, v in inputs.items()}))
        return DeviceUpdate(Sink.Outputs(), None)
