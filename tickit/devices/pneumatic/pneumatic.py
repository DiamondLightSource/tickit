from typing import Awaitable, Callable, Dict

from softioc import builder

from tickit.adapters.epicsadapter import EpicsAdapter, InputRecord, OutputRecord
from tickit.core.device import ConfigurableDevice, DeviceUpdate
from tickit.core.typedefs import SimTime
from tickit.utils.compat.typing_compat import TypedDict


class Pneumatic(ConfigurableDevice):
    """Pneumatic Device with movement controls."""

    Output = TypedDict("Output", {"output": float})

    def __init__(
        self,
        initial_speed: float = 2.5,
        initial_state: bool = False,
    ) -> None:
        """Initialise a Pneumatic object."""
        self.speed: float = initial_speed
        self.state: bool = initial_state
        self.moving: bool = False
        self.time_at_last_update: float = 0.0

    def set_speed(self, speed: float) -> None:
        """Set the speed of movement for the device."""
        self.speed = speed

    def get_speed(self) -> float:
        """Get the speed of movement of the device."""
        return self.speed

    def set_state(self, value) -> None:
        """Toggles the target state of the device."""
        self.moving = True
        if self.state:
            self.target_state = False
        else:
            self.target_state = True

    def get_state(self) -> bool:
        """Gets the current state of the device."""
        return self.state

    def update(self, time: SimTime, inputs: dict) -> DeviceUpdate:
        """Run the update logic for the device.

        If the device is moving then the state of the device is updated. Otherwise nothing changes. In either case the
        current state of the device is returned.
        """
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
    """An adapter for the Pneumatic class, connecting it to an external messaging protocol."""

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
        """Initialise a PneumaticAdapter object."""
        super().__init__(db_file, ioc_name)
        self._device = device
        self.raise_interrupt = raise_interrupt

        self.interrupt_records = {}

    async def run_forever(self) -> None:
        """Run the device indefinitely."""
        self.build_ioc()

    async def callback(self, value) -> None:
        """Set the state of the device and await a response."""
        self._device.set_state(value)
        await self.raise_interrupt()

    def records(self) -> None:
        """Adds a record of the current state to the mapping of interrupting records."""
        self.state_rbv = builder.boolIn("FILTER_RBV")
        self.state_record = builder.boolOut(
            "FILTER", initial_value=False, on_update=self.callback
        )
        self.link_input_on_interrupt(self.state_rbv, self._device.get_state)
