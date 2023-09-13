from typing import TypedDict

import pydantic.v1.dataclasses
from softioc import builder

from tickit.adapters.epics import EpicsAdapter
from tickit.adapters.io import EpicsIo, TcpIo
from tickit.adapters.specifications import RegexCommand
from tickit.adapters.tcp import CommandAdapter
from tickit.core.adapter import AdapterContainer
from tickit.core.components.component import Component, ComponentConfig
from tickit.core.components.device_component import DeviceComponent
from tickit.core.device import Device, DeviceUpdate
from tickit.core.typedefs import SimTime
from tickit.utils.byte_format import ByteFormat


class IsolatedBoxDevice(Device):
    """Isolated device which stores a float value.

    The device has no inputs or outputs and interacts solely through adapters.
    """

    class Inputs(TypedDict):
        ...

    class Outputs(TypedDict):
        ...

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


class IsolatedBoxTCPAdapter(CommandAdapter):
    """A composed adapter which allows getting and setting the value of the device."""

    device: IsolatedBoxDevice
    _byte_format: ByteFormat = ByteFormat(b"%b\r\n")

    def __init__(
        self,
        device: IsolatedBoxDevice,
    ) -> None:
        super().__init__()
        self.device = device

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

    def __init__(self, device: IsolatedBoxDevice) -> None:
        super().__init__()
        self.device = device

    async def callback(self, value) -> None:
        """Device callback function.

        Args:
            value (float): The value to set the device to.
        """
        self.device.set_value(value)
        await self.interrupt()

    def on_db_load(self) -> None:
        """Customises records that have been loaded in to suit the simulation."""
        builder.aOut("VALUE", initial_value=self.device.value, on_update=self.callback)
        self.link_input_on_interrupt(builder.aIn("VALUE_RBV"), self.device.get_value)


@pydantic.v1.dataclasses.dataclass
class IsolatedBox(ComponentConfig):
    """Isolated box device you can change the value of either over TCP or via EPICS."""

    initial_value: float
    port: int
    ioc_name: str
    host: str = "localhost"

    def __call__(self) -> Component:  # noqa: D102
        device = IsolatedBoxDevice(
            initial_value=self.initial_value,
        )
        adapters = [
            AdapterContainer(
                IsolatedBoxTCPAdapter(device),
                TcpIo(
                    self.host,
                    self.port,
                ),
            ),
            AdapterContainer(
                IsolatedBoxEpicsAdapter(device),
                EpicsIo("ISOLATED_IOC"),
            ),
        ]
        return DeviceComponent(
            name=self.name,
            device=device,
            adapters=adapters,
        )
