from dataclasses import dataclass

from tickit.adapters.composed import ComposedAdapter
from tickit.adapters.interpreters.command import CommandInterpreter, RegexCommand
from tickit.adapters.servers.tcp import TcpServer
from tickit.core.adapter import Server
from tickit.core.components.component import Component, ComponentConfig
from tickit.core.components.device_simulation import DeviceSimulation
from tickit.core.device import Device, DeviceUpdate
from tickit.core.typedefs import SimTime
from tickit.utils.byte_format import ByteFormat
from tickit.utils.compat.typing_compat import TypedDict


class IoBoxDevice(Device):
    """An isolated toy device which stores a message.

    The device takes no inputs and produces no outputs. It interacts exclusively with
    an adapter which sets incoming messages to it and reads stored messages from it.
    """

    #: An empty typed mapping of device inputs
    Inputs: TypedDict = TypedDict("Inputs", {})
    #: A typed mapping containing the current output value
    Outputs: TypedDict = TypedDict("Outputs", {})

    def __init__(self, inital_value: str = "Hello") -> None:
        """The IoBox constructor, sets intial message value."""
        self.message = inital_value

    def update(self, time: SimTime, inputs: Inputs) -> DeviceUpdate[Outputs]:
        """The update method which produces an output mapping containing the observed
        value.

        For this device the DeviceUpdate produces no outputs.

        Args:
            time (SimTime): The current simulation time (in nanoseconds).
            inputs (State): A mapping of inputs to the device and their values.

        Returns:
            DeviceUpdate[Outputs]:
                The produced update event which contains the observed value, in this
                case nothing is provided. The device never requests a callback.
        """
        return DeviceUpdate(IoBoxDevice.Outputs(), None)


class IOBoxAdapater(ComposedAdapter):
    """A Composed adapter for setting and getting the device property."""

    device: IoBoxDevice

    def __init__(
        self,
        server: Server,
    ) -> None:
        """Constructor of the IoBoc Adapter, builds the configured server.

        Args:
            server (Server): The immutable data container used to configure a
                server.
        """
        super().__init__(
            server,
            CommandInterpreter(),
        )

    @RegexCommand(r"m=([a-zA-Z0-9_!.?-]+)", interrupt=True, format="utf-8")
    async def set_message(self, value: str) -> None:
        """Regex string command which sets the value of the message.

        Args:
            value (str): The new value of the message.
        """
        self.device.message = value

    @RegexCommand(r"m\?", format="utf-8")
    async def get_message(self) -> bytes:
        """Regex string command which returns the utf-8 encoded value of the message.

        Returns:
            bytes: The utf-8 encoded value of the message.
        """
        return str(self.device.message).encode("utf-8")


@dataclass
class IoBox(ComponentConfig):
    """IO Box you can talk to over TCP."""

    host: str = "localhost"
    port: int = 25565
    format: ByteFormat = ByteFormat(b"%b\r\n")

    def __call__(self) -> Component:  # noqa: D102
        return DeviceSimulation(
            name=self.name,
            device=IoBoxDevice(),
            adapters=[IOBoxAdapater(TcpServer(self.host, self.port, self.format))],
        )
