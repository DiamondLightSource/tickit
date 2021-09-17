from random import uniform
from typing import Awaitable, Callable, Dict

from softioc import builder

from tickit.adapters.epicsadapter import EpicsAdapter, InputRecord, OutputRecord
from tickit.core.device import ConfigurableDevice, DeviceUpdate
from tickit.core.typedefs import SimTime, State
from tickit.utils.compat.typing_compat import TypedDict


class Femto(ConfigurableDevice):
    """
    Electronic signal amplifier
    """

    Output = TypedDict("Output", {"current": float})

    def __init__(
        self,
        initial_gain: float = 2.5,
        initial_current: float = 0.0,
    ) -> None:
        self.gain: float = initial_gain
        self._current: float = initial_current

    def set_gain(self, gain: float) -> None:
        self.gain = gain

    def get_gain(self) -> float:
        return self.gain

    def set_current(self, current: float) -> None:
        self._current = current * self.gain

    def get_current(self) -> float:
        return self._current

    # Changed State for dict
    def update(self, time: SimTime, inputs: dict) -> DeviceUpdate:
        current_value = inputs.get("input", None)
        if current_value is not None:
            self.set_current(current_value)

        return DeviceUpdate(Femto.Output(current=self.gain), None)


class CurrentDevice(ConfigurableDevice):
    Output = TypedDict("Output", {"output": float})

    def __init__(self, callback_period: int = int(1e9)) -> None:
        self.callback_period = SimTime(callback_period)

    def update(self, time: SimTime, inputs: State) -> DeviceUpdate:
        output = uniform(0.1, 200.1)
        print(
            "Output! (delta: {}, inputs: {}, output: {})".format(time, inputs, output)
        )
        return DeviceUpdate(
            CurrentDevice.Output(output=output), SimTime(time + self.callback_period)
        )


class FemtoAdapter(EpicsAdapter):

    current_record: InputRecord
    input_record: InputRecord
    output_record: OutputRecord

    def __init__(
        self,
        device: Femto,
        raise_interrupt: Callable[[], Awaitable[None]],
        db_file: str = "record.db",
        ioc_name: str = "FEMTO",
    ):
        super().__init__(db_file, ioc_name)
        self._device = device
        self.raise_interrupt = raise_interrupt

        self.interrupt_records: Dict[InputRecord, Callable] = {}

    async def run_forever(self) -> None:
        self.build_ioc()

    async def callback(self, value) -> None:
        print("Callback", value)
        self._device.set_gain(value)
        await self.raise_interrupt()

    def records(self) -> None:

        self.input_record = builder.aIn("GAIN_RBV")
        self.output_record = builder.aOut(
            "GAIN", initial_value=self._device.get_gain(), on_update=self.callback
        )

        self.current_record = builder.aIn("CURRENT")

        self.link_input_on_interrupt(self.input_record, self._device.get_gain)
        self.link_input_on_interrupt(self.current_record, self._device.get_current)
