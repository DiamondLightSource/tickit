import asyncio
import json
import logging
from typing import Iterable, Optional, Protocol, runtime_checkable

import aiozmq
import zmq
from pydantic.v1 import BaseModel

from tickit.adapters.zmq import (
    ZeroMqMessage,
    ZeroMqPushAdapter,
    _MessagePart,
    _SerializableMessagePart,
    _ZeroMqInternalMessage,
)
from tickit.core.adapter import AdapterIo, RaiseInterrupt

LOGGER = logging.getLogger(__name__)


@runtime_checkable
class SocketFactory(Protocol):
    async def __call__(self, __host: str, __port: int) -> aiozmq.ZmqStream:
        ...


async def create_zmq_push_socket(host: str, port: int) -> aiozmq.ZmqStream:
    addr = f"tcp://{host}:{port}"
    return await aiozmq.create_zmq_stream(zmq.PUSH, connect=addr, bind=addr)


class ZeroMqPushIo(AdapterIo[ZeroMqPushAdapter]):
    """AdapterIo for a ZeroMQ data stream."""

    _host: str
    _port: int
    _socket: Optional[aiozmq.ZmqStream]
    _socket_factory: SocketFactory
    _socket_lock: asyncio.Lock
    _task: Optional[asyncio.Task]

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 5555,
        socket_factory: SocketFactory = create_zmq_push_socket,
    ) -> None:
        """Initialize with default values."""
        super().__init__()
        self._host = host
        self._port = port
        self._socket = None
        self._socket_factory = socket_factory
        self._socket_lock = asyncio.Lock()
        self._task = None

    async def setup(
        self, adapter: ZeroMqPushAdapter, raise_interrupt: RaiseInterrupt
    ) -> None:
        try:
            await self._ensure_socket()
            self._task = asyncio.create_task(self.send_messages_forever(adapter))
        except asyncio.CancelledError:
            await self.shutdown()

    async def shutdown(self) -> None:
        if self._task:
            self._task.cancel()
        if self._socket is not None:
            self._socket.close()
            await self._socket.drain()

    async def send_messages_forever(self, adapter: ZeroMqPushAdapter) -> None:
        while True:
            message = await adapter.next_message()
            await self.send_message(message)

    def send_message_sequence_soon(
        self,
        messages: Iterable[ZeroMqMessage],
    ) -> None:
        async def send_message_sequence() -> None:
            for message in messages:
                await self.send_message(message)

        asyncio.create_task(send_message_sequence())

    async def send_message(self, message: ZeroMqMessage) -> None:
        socket = await self._ensure_socket()
        serialized = self._serialize(message)
        socket.write(serialized)
        await socket.drain()

    async def _ensure_socket(self) -> aiozmq.ZmqStream:
        async with self._socket_lock:
            if self._socket is None:
                self._socket = await self._socket_factory(self._host, self._port)
        return self._socket

    def _serialize(self, message: ZeroMqMessage) -> _ZeroMqInternalMessage:
        return list(map(self._serialize_part, message))

    def _serialize_part(self, part: _SerializableMessagePart) -> _MessagePart:
        if isinstance(part, BaseModel):
            return self._serialize_part(part.dict())
        elif isinstance(part, dict) or isinstance(part, str):
            return self._serialize_part(json.dumps(part).encode("utf_8"))
        elif isinstance(part, bytes):
            return part
        else:
            raise TypeError(f"Message: {part} is not serializable")
