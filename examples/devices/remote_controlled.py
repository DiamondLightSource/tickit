import asyncio
import logging
import struct
from typing import AsyncIterable, Optional, TypedDict

import pydantic.v1.dataclasses

from tickit.adapters.io.tcp_io import TcpIo
from tickit.adapters.specifications import RegexCommand
from tickit.adapters.tcp import CommandAdapter
from tickit.core.adapter import AdapterContainer
from tickit.core.components.component import Component, ComponentConfig
from tickit.core.components.device_component import DeviceComponent
from tickit.core.device import Device, DeviceUpdate
from tickit.core.typedefs import SimTime
from tickit.utils.byte_format import ByteFormat

LOGGER = logging.getLogger(__name__)


class RemoteControlledDevice(Device):
    """A trivial toy device which is controlled by an adapter."""

    #: An empty typed mapping of device inputs
    class Inputs(TypedDict):
        ...

    #: A typed mapping containing the 'observed' output value
    class Outputs(TypedDict):
        observed: float

    def __init__(
        self,
        initial_observed: float = 0,
        initial_unobserved: float = 42,
        initial_hidden: float = 3.14,
    ) -> None:
        """A RemoteControlled constructor which configures various initial values.

        Args:
            initial_observed (float): The initial value of the observed device property.
                Defaults to 0.
            initial_unobserved (float): The initial value of the unobserved device
                property. Defaults to 42.
            initial_hidden (float): The initial value of the hidden device property.
                Defaults to 3.14.
        """
        self.observed = initial_observed
        self.unobserved = initial_unobserved
        self.hidden = initial_hidden

    def update(self, time: SimTime, inputs: Inputs) -> DeviceUpdate[Outputs]:
        """Produces an output mapping containing the observed value.

        Args:
            time (SimTime): The current simulation time (in nanoseconds).
            inputs (State): A mapping of inputs to the device and their values.

        Returns:
            DeviceUpdate[Outputs]:
                The produced update event which contains the observed value, the device
                never requests a callback.
        """
        return DeviceUpdate(self.Outputs(observed=self.observed), None)


class RemoteControlledAdapter(CommandAdapter):
    """A trivial composed adapter which gets and sets device properties."""

    device: RemoteControlledDevice
    _byte_format: ByteFormat = ByteFormat(b"%b\r\n")

    def __init__(self, device: RemoteControlledDevice, format: ByteFormat) -> None:
        super().__init__()
        self.device = device
        self._byte_format = format

    async def on_connect(self) -> AsyncIterable[Optional[bytes]]:
        """Continiously sends the unobserved value to the client.

        Returns:
            AsyncIterable[bytes]:
                An asynchronous iterable which regularly outputs the unobserved value.
        """
        while True:
            await asyncio.sleep(5.0)
            yield f"U is {self.device.unobserved}".encode("utf-8")

    @RegexCommand(b"\x01")
    async def get_observed_bytes(self) -> bytes:
        """A regex bytes command which returns the byte encoded value of observed.

        Returns:
            bytes: The big endian float encoded value of observed.
        """
        return struct.pack(">f", self.device.observed)

    @RegexCommand(r"O", format="utf-8")
    async def get_observed_str(self) -> bytes:
        """A regex string command which returns the utf-8 encoded value of observed.

        Returns:
            bytes: The utf-8 encoded value of observed.
        """
        return str(self.device.observed).encode("utf-8")

    @RegexCommand(b"\x01(.{4})", interrupt=True)
    async def set_observed_bytes(self, value: bytes) -> bytes:
        """A regex bytes command which sets and echos the value of observed.

        Args:
            value (bytes): The new big endian float encoded value of observed.

        Returns:
            bytes: The big endian float encoded value of observed.
        """
        self.device.observed = struct.unpack(">f", value)[0]
        return struct.pack(">f", self.device.observed)

    @RegexCommand(r"O=(\d+\.?\d*)", interrupt=True, format="utf-8")
    async def set_observed_str(self, value: float) -> bytes:
        """A regex string command which sets and echos the value of observed.

        Args:
            value (int): The new value of observed.

        Returns:
            bytes: The utf-8 encoded value of observed.
        """
        self.device.observed = value
        return f"Observed set to {self.device.observed}".encode("utf-8")

    @RegexCommand(b"\x02")
    async def get_unobserved_bytes(self) -> bytes:
        """A regex bytes command which returns the byte encoded value of unobserved.

        Returns:
            bytes: The big endian float encoded value of unobserved.
        """
        return struct.pack(">f", self.device.unobserved)

    @RegexCommand(r"U", format="utf-8")
    async def get_unobserved_str(self) -> bytes:
        """A regex string command which returns the utf-8 encoded value of unobserved.

        Returns:
            bytes: The utf-8 encoded value of unobserved.
        """
        return str(self.device.unobserved).encode("utf-8")

    @RegexCommand(b"\x02(.{4})")
    async def set_unobserved_bytes(self, value: bytes) -> bytes:
        """A regex bytes command which sets and echos the value of unobserved.

        Args:
            value (bytes): The new big endian float encoded value of unobserved.

        Returns:
            bytes: The big endian float encoded value of unobserved.
        """
        self.device.unobserved = struct.unpack(">f", value)[0]
        return struct.pack(">f", self.device.unobserved)

    @RegexCommand(r"U=(\d+\.?\d*)", format="utf-8")
    async def set_unobserved_str(self, value: float) -> bytes:
        """A regex string command which sets and echos the value of unobserved.

        Args:
            value (int): The new value of unobserved.

        Returns:
            bytes: The utf-8 encoded value of unobserved.
        """
        self.device.unobserved = value
        return f"Unobserved set to {self.device.unobserved}".encode("utf-8")

    @RegexCommand(chr(0x1F95A), format="utf-8")
    async def misc(self) -> bytes:
        """A regex string command which returns a utf-8 encoded character.

        Returns:
            bytes: A utf-8 encoded character.
        """
        return chr(0x1F430).encode("utf-8")

    @RegexCommand(r"H=(\d+\.?\d*)", format="utf-8")
    async def set_hidden(self, value: float) -> None:
        """A regex string command which sets the value of hidden.

        Args:
            value (float): The new value of hidden.
        """
        LOGGER.info(f"Hidden set to {self.device.hidden}")

    @RegexCommand(r"H", format="utf-8")
    async def get_hidden(self) -> None:
        """A regex string command which returns nothing, hidden cannot be shown."""
        pass

    @RegexCommand(r"O\?(\d+)", format="utf-8")
    async def yield_observed(self, n: int = 10) -> AsyncIterable[bytes]:
        """A regex string command which sends observed numerous times.

        Args:
            n (int): The number of times which observed should be sent. Defaults to 10.

        Returns:
            AsyncIterable[bytes]:
                An asynchronous iterable which yields the value of observed the
                specified number of times with a fixed delay.
        """
        for i in range(1, int(n)):
            await asyncio.sleep(1.0)
            yield f"Observed is {self.device.observed}".encode("utf-8")


@pydantic.v1.dataclasses.dataclass
class RemoteControlled(ComponentConfig):
    """Thing you can poke over TCP."""

    format: ByteFormat

    def __call__(self) -> Component:  # noqa: D102
        device = RemoteControlledDevice()
        adapters = [
            AdapterContainer(
                RemoteControlledAdapter(
                    device,
                    format=self.format,
                ),
                TcpIo(
                    host="localhost",
                    port=25565,
                ),
            )
        ]
        return DeviceComponent(
            name=self.name,
            device=device,
            adapters=adapters,
        )
