from typing import Awaitable, Callable, Dict

from softioc import builder

from tickit.adapters.epicsadapter import EpicsAdapter, InputRecord, OutputRecord
from tickit.core.device import ConfigurableDevice, DeviceUpdate
from tickit.core.typedefs import SimTime
from tickit.utils.compat.typing_compat import TypedDict


class Pneumatic(ConfigurableDevice):

    Output = TypedDict("Output", {"output": float})

    def __init__(
        self,
        initial_speed: float = 2.5,
        initial_state: bool = False,
    ) -> None:
        self.speed: float = initial_speed
        self.state: bool = initial_state
        self.moving: bool = False
        self.time_at_last_update: float = 0.0

    def set_speed(self, speed: float) -> None:
        self.speed = speed

    def get_speed(self) -> float:
        return self.speed

    def set_state(self, value) -> None:
        self.moving = True
        if self.state:
            self.target_state = False
        else:
            self.target_state = True

    def get_state(self) -> bool:
        return self.state

    def update(self, time: SimTime, inputs: dict) -> DeviceUpdate:
        if self.moving:
            callback_period = SimTime(int(1e9 / self.speed))
            self.state = self.target_state
            self.moving = False
            return DeviceUpdate(
                Pneumatic.Output(output=self.state),
                callback_period,
            )
        else:
            return DeviceUpdate(Pneumatic.Output(output=self.state), None)


class PneumaticAdapter(EpicsAdapter):

    current_record: InputRecord
    input_record: InputRecord
    output_record: OutputRecord

    interrupt_records: Dict[InputRecord, Callable]

    def __init__(
        self,
        device: Pneumatic,
        raise_interrupt: Callable[[], Awaitable[None]],
        db_file: str,
        ioc_name: str = "PNEUMATIC",
    ) -> None:
        super().__init__(db_file, ioc_name)
        self._device = device
        self.raise_interrupt = raise_interrupt

        self.interrupt_records = {}

    async def run_forever(self) -> None:
        self.build_ioc()

    async def callback(self, value) -> None:
        self._device.set_state(value)
        await self.raise_interrupt()

    def on_db_load(self):

        self.state_rbv = builder.boolIn("FILTER_RBV")

        self.state_record = builder.boolOut(
            "FILTER", initial_value=False, on_update=self.callback
        )
        self.link_input_on_interrupt(self.state_rbv, self._device.get_state)
