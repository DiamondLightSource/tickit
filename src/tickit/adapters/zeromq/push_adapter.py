import asyncio
import json
import logging
from typing import Any, Iterable, Mapping, Optional, Sequence, Union

import aiozmq
import zmq
from pydantic.v1 import BaseModel

from tickit.core.adapter import Adapter, RaiseInterrupt
from tickit.core.device import Device

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


class ZeroMqPushAdapter(Adapter):
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
        self,
        device: Device,
        raise_interrupt: RaiseInterrupt,
    ) -> None:
        """Runs the ZeroMQ adapter continuously."""
        await super().run_forever(device, raise_interrupt)
        await self._ensure_socket()

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
        if self._socket is None:
            addr = f"tcp://{self._host}:{self._port}"
            self._socket = await aiozmq.create_zmq_stream(
                zmq.PUSH, connect=addr, bind=addr
            )
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
