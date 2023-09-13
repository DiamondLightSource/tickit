import pydantic.v1.dataclasses
from softioc import builder
from typing_extensions import TypedDict

from tickit.adapters.epics import EpicsAdapter
from tickit.adapters.io.epics_io import EpicsIo
from tickit.adapters.io.tcp_io import TcpIo
from tickit.adapters.specifications import RegexCommand
from tickit.adapters.tcp import CommandAdapter
from tickit.core.adapter import AdapterContainer
from tickit.core.components.component import Component, ComponentConfig
from tickit.core.components.device_component import DeviceComponent
from tickit.core.device import Device, DeviceUpdate
from tickit.core.typedefs import SimTime
from tickit.utils.byte_format import ByteFormat


class AmplifierDevice(Device):
    """Amplifier device which multiplies an input signal by an amplification value."""

    class Inputs(TypedDict):
        initial_signal: float

    class Outputs(TypedDict):
        amplified_signal: float

    def __init__(self, initial_amplification: float = 2) -> None:
        """Amplifier constructor which configures the initial amplification.

        Args:
            initial_amplification (float): The inital value of amplification of the
                device. Defaults to 2.
        """
        self.amplification = initial_amplification

    def update(self, time: SimTime, inputs: Inputs) -> DeviceUpdate[Outputs]:
        """Update method that amplifies input signal and produces scaled output signal.

        This update method multiplies the input signal by the amplification value and
        returns a device update with this new scaled signal as an output.

        Args:
            time (SimTime): The current simulation time (in nanoseconds).
            inputs (State): A mapping of inputs to the device and their values.

        Returns:
            DeviceUpdate[Outputs]:
                The produced update event which contains the value of the new amplified
                signal.
        """
        amplified_value = inputs["initial_signal"] * self.amplification
        return DeviceUpdate(self.Outputs(amplified_signal=amplified_value), None)

    def set_amplification(self, value: float) -> None:
        self.amplification = value

    def get_amplification(self) -> float:
        return self.amplification


class AmplifierAdapter(CommandAdapter):
    """A TCP adapter which gets and sets the value of amplification."""

    device: AmplifierDevice
    _byte_format: ByteFormat = ByteFormat(b"%b\r\n")

    def __init__(self, device: AmplifierDevice) -> None:
        super().__init__()
        self.device = device

    @RegexCommand(r"A\?", False, "utf-8")
    async def get_amplification(self) -> bytes:
        """Regex string command which returns the utf-8 encoded value of amplification.

        Returns:
            bytes: The utf-8 encoded value of amplification.
        """
        return str(self.device.amplification).encode("utf-8")

    @RegexCommand(r"A=(\d+\.?\d*)", True, "utf-8")
    async def set_amplification(self, amplification: float) -> None:
        """Regex string command which sets the value of amplification.

        Args:
            amplification (float): The desired value of amplification.
        """
        self.device.amplification = amplification


class AmplifierEpicsAdapter(EpicsAdapter):
    """A EPICS adapter which gets and sets the value of amplification."""

    device: AmplifierDevice

    def __init__(self, device: AmplifierDevice) -> None:
        super().__init__()
        self.device = device

    async def callback(self, value) -> None:
        """Device callback function.

        Args:
            value (float): The value to set the device to.
        """
        self.device.set_amplification(value)
        await self.interrupt()

    def on_db_load(self) -> None:
        """Customises records that have been loaded in to suit the simulation."""
        builder.aOut(
            "VALUE",
            initial_value=self.device.amplification,
            on_update=self.callback,
        )
        self.link_input_on_interrupt(
            builder.aIn("VALUE_RBV"), self.device.get_amplification
        )


@pydantic.v1.dataclasses.dataclass
class Amplifier(ComponentConfig):
    """Amplifier you can set the amplification value of over TCP."""

    initial_amplification: int
    host: str = "localhost"
    port: int = 25565

    def __call__(self) -> Component:  # noqa: D102
        device = AmplifierDevice(
            initial_amplification=self.initial_amplification,
        )
        adapters = [
            AdapterContainer(
                AmplifierAdapter(device),
                TcpIo(
                    self.host,
                    self.port,
                ),
            ),
            AdapterContainer(
                AmplifierEpicsAdapter(device),
                EpicsIo("AMP_IOC"),
            ),
        ]
        return DeviceComponent(
            name=self.name,
            device=device,
            adapters=adapters,
        )
