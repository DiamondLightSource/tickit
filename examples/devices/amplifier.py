from dataclasses import dataclass

from typing_extensions import TypedDict

from tickit.adapters.composed import ComposedAdapter
from tickit.adapters.interpreters.command.command_interpreter import CommandInterpreter
from tickit.adapters.interpreters.command.regex_command import RegexCommand
from tickit.adapters.servers.tcp import TcpServer
from tickit.core.components.component import Component, ComponentConfig
from tickit.core.components.device_simulation import DeviceSimulation
from tickit.core.device import Device, DeviceUpdate
from tickit.core.typedefs import SimTime
from tickit.utils.byte_format import ByteFormat


class AmplifierDevice(Device):
    """Amplifier device which multiplies an input signal by an amplification value."""

    Inputs: TypedDict = TypedDict("Inputs", {"initial_signal": float})
    Outputs: TypedDict = TypedDict("Outputs", {"amplified_signal": float})

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


class AmplifierAdapter(ComposedAdapter):
    """A composed adapter which gets and sets the value of amplification."""

    device: AmplifierDevice

    def __init__(
        self,
        host: str = "localhost",
        port: int = 25565,
    ) -> None:
        """Instantiate a composed amplifier adapter with a configured TCP server.

        Args:
            host (Optional[str]): The host address of the TcpServer. Defaults to
                "localhost".
            port (Optional[int]): The bound port of the TcpServer. Defaults to 25565.

        """
        super().__init__(
            TcpServer(host, port, ByteFormat(b"%b\r\n")),
            CommandInterpreter(),
        )

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


@dataclass
class Amplifier(ComponentConfig):
    """Amplifier you can set the amplification value of over TCP."""

    initial_amplification: int

    def __call__(self) -> Component:  # noqa: D102
        return DeviceSimulation(
            name=self.name,
            device=AmplifierDevice(
                initial_amplification=self.initial_amplification,
            ),
            adapters=[AmplifierAdapter()],
        )
