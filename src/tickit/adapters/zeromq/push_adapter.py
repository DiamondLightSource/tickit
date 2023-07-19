import asyncio
import json
import logging
from typing import (
    Any,
    Iterable,
    Mapping,
    Optional,
    Protocol,
    Sequence,
    Union,
    runtime_checkable,
)

import aiozmq
import zmq

from tickit.core.adapter import Adapter, RaiseInterrupt
from tickit.core.device import Device
from tickit.utils.compat.pydantic_compat import BaseModel

LOGGER = logging.getLogger(__name__)


_MessagePart = Union[bytes, zmq.Frame, memoryview]
_SerializableMessagePart = Union[
    _MessagePart,
    str,
    Mapping[str, Any],
    BaseModel,
]

_ZeroMqInternalMessage = Sequence[_MessagePart]
ZeroMqMessage = Sequence[_SerializableMessagePart]
# SocketFactory = Callable[[], Awaitable[aiozmq.ZmqStream]]


@runtime_checkable
class SocketFactory(Protocol):
    async def __call__(self, __host: str, __port: int) -> aiozmq.ZmqStream:
        ...


async def create_zmq_push_socket(host: str, port: int) -> aiozmq.ZmqStream:
    addr = f"tcp://{host}:{port}"
    return await aiozmq.create_zmq_stream(zmq.PUSH, connect=addr, bind=addr)


class ZeroMqPushAdapter(Adapter):
    """An adapter for a ZeroMQ data stream."""

    _host: str
    _port: int
    _socket: Optional[aiozmq.ZmqStream]
    _socket_factory: SocketFactory
    _socket_lock: asyncio.Lock

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

    async def run_forever(
        self,
        device: Device,
        raise_interrupt: RaiseInterrupt,
    ) -> None:
        """Runs the ZeroMQ adapter continuously."""
        await super().run_forever(device, raise_interrupt)

        try:
            await self._ensure_socket()
        except asyncio.CancelledError:
            if self._socket is not None:
                self._socket.close()
                await self._socket.drain()

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
