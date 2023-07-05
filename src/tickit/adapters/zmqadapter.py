import asyncio
import logging
from typing import Iterable, Optional, Sequence

import aiozmq
import zmq

from tickit.core.adapter import Adapter, RaiseInterrupt
from tickit.core.device import Device

LOGGER = logging.getLogger(__name__)


class ZeroMQAdapter(Adapter):
    """An adapter for a ZeroMQ data stream."""

    _host: str
    _port: int
    _socket: Optional[aiozmq.ZmqStream]

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 5555,
    ) -> None:
        """Initialize with default values."""
        super().__init__()
        self._host = host
        self._port = port
        self._socket = None
        self._message_queue = None

    async def run_forever(
        self, device: Device, raise_interrupt: RaiseInterrupt
    ) -> None:
        """Runs the ZeroMQ adapter continuously."""
        await super().run_forever(device, raise_interrupt)
        await self._ensure_socket()

    def send_message_sequence_soon(self, messages: Iterable[Sequence[bytes]]) -> None:
        async def send_message_sequence() -> None:
            for message in messages:
                await self.send_message(message)

        asyncio.create_task(send_message_sequence())

    async def send_message(self, message: Sequence[bytes]) -> None:
        socket = await self._ensure_socket()
        socket.write(message)
        await socket.drain()

    async def _ensure_socket(self) -> aiozmq.ZmqStream:
        if self._socket is None:
            addr = f"tcp://{self._host}:{self._port}"
            self._socket = await aiozmq.create_zmq_stream(
                zmq.PUSH, connect=addr, bind=addr
            )
        return self._socket
