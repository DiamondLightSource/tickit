from random import randint

from tickit.core.device import ConfigurableDevice, DeviceUpdate
from tickit.core.typedefs import SimTime
from tickit.utils.compat.typing_compat import TypedDict


class Trampoline(ConfigurableDevice):
    Inputs: TypedDict = TypedDict("Inputs", {})
    Outputs: TypedDict = TypedDict("Outputs", {})

    def __init__(self, callback_period: int = int(1e9)) -> None:
        self.callback_period = SimTime(callback_period)

    def update(
        self, time: SimTime, inputs: "Trampoline.Inputs"
    ) -> DeviceUpdate["Trampoline.Outputs"]:
        print("Boing! ({}, {})".format(time, inputs))
        return DeviceUpdate(Trampoline.Outputs(), self.callback_period)


class RandomTrampoline(ConfigurableDevice):
    Inputs: TypedDict = TypedDict("Inputs", {})
    Outputs: TypedDict = TypedDict("Outputs", {"output": int})

    def __init__(self, callback_period: int = int(1e9)) -> None:
        self.callback_period = SimTime(callback_period)

    def update(
        self, time: SimTime, inputs: "RandomTrampoline.Inputs"
    ) -> DeviceUpdate["RandomTrampoline.Outputs"]:
        output = randint(0, 255)
        print("Boing! (delta: {}, inputs: {}, output: {})".format(time, inputs, output))
        return DeviceUpdate(
            RandomTrampoline.Outputs(output=output), self.callback_period
        )
