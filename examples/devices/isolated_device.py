from dataclasses import dataclass
from typing import TypedDict

from softioc import builder

from tickit.adapters.composed import ComposedAdapter
from tickit.adapters.epicsadapter.adapter import EpicsAdapter
from tickit.adapters.interpreters.command.command_interpreter import CommandInterpreter
from tickit.adapters.interpreters.command.regex_command import RegexCommand
from tickit.adapters.servers.tcp import TcpServer
from tickit.core.components.component import Component, ComponentConfig
from tickit.core.components.device_simulation import DeviceSimulation
from tickit.core.device import Device, DeviceUpdate
from tickit.core.typedefs import SimTime
from tickit.utils.byte_format import ByteFormat


class IsolatedBoxDevice(Device):
    """Isolated device which stores a float value.

    The device has no inputs or outputs and interacts solely through adapters.
    """

    Inputs: TypedDict = TypedDict("Inputs", {})
    Outputs: TypedDict = TypedDict("Outputs", {})

    def __init__(self, initial_value: float = 2) -> None:
        """Constructor which configures the initial value

        Args:
            initial_value (int): The inital value of the device. Defaults to 2.
        """
        self.value = initial_value

    def update(self, time: SimTime, inputs: Inputs) -> DeviceUpdate[Outputs]:
        """Update method that outputs nothing.

        Args:
            time (SimTime): The current simulation time (in nanoseconds).
            inputs (State): A mapping of inputs to the device and their values.

        Returns:
            DeviceUpdate[Outputs]:
                The produced update event which contains nothing.
        """
        return DeviceUpdate(self.Outputs(), None)

    def get_value(self):
        """Returns the value set for the device, required for the epics adapter."""
        return self.value

    def set_value(self, value: float):
        """Sets the value for the device, required for the epics adapter."""
        self.value = value


class IsolatedBoxTCPAdapter(ComposedAdapter):
    """A composed adapter which allows getting and setting the value of the device."""

    device: IsolatedBoxDevice

    def __init__(
        self,
        host: str = "localhost",
        port: int = 25565,
    ) -> None:
        """Instantiate a composed adapter with a configured TCP server.

        Args:
            host (Optional[str]): The host address of the TcpServer. Defaults to
                "localhost".
            port (Optional[int]): The bound port of the TcpServer. Defaults to 25565.

        """
        super().__init__(
            TcpServer(host, port, ByteFormat(b"%b\r\n")),
            CommandInterpreter(),
        )

    @RegexCommand(r"v\?", False, "utf-8")
    async def get_value(self) -> bytes:
        """Regex string command which returns the utf-8 encoded value.

        Returns:
            bytes: The utf-8 encoded value.
        """
        return str(self.device.value).encode("utf-8")

    @RegexCommand(r"v=(\d+\.?\d*)", True, "utf-8")
    async def set_value(self, value: float) -> None:
        """Regex string command which sets the value

        Args:
            value (float): The desired new value.
        """
        self.device.value = value


class IsolatedBoxEpicsAdapter(EpicsAdapter):
    """IsolatedBox adapter to allow interaction using an EPICS interface."""

    device: IsolatedBoxDevice

    async def callback(self, value) -> None:
        """Device callback function.

        Args:
            value (float): The value to set the device to.
        """
        self.device.set_value(value)
        await self.raise_interrupt()

    def on_db_load(self) -> None:
        """Customises records that have been loaded in to suit the simulation."""
        builder.aOut("VALUE", initial_value=self.device.value, on_update=self.callback)
        self.link_input_on_interrupt(builder.aIn("VALUE_RBV"), self.device.get_value)


@dataclass
class IsolatedBox(ComponentConfig):
    """Isolated box device you can change the value of either over TCP or via EPICS."""

    initial_value: float
    port: int
    ioc_name: str
    host: str = "localhost"
    db_file_path: str = "src/../examples/devices/isolated_record.db"

    def __call__(self) -> Component:  # noqa: D102
        return DeviceSimulation(
            name=self.name,
            device=IsolatedBoxDevice(
                initial_value=self.initial_value,
            ),
            adapters=[
                IsolatedBoxTCPAdapter(host=self.host, port=self.port),
                IsolatedBoxEpicsAdapter(
                    db_file=self.db_file_path,
                    ioc_name=self.ioc_name,
                ),
            ],
        )
