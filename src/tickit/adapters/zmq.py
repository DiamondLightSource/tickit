import asyncio
from typing import Optional

from tickit.adapters.io.zeromq_push_io import ZeroMqMessage


class ZeroMqPushAdapter:
    """An adapter interface for the ZeroMqPushIo."""

    _message_queue: Optional[asyncio.Queue]

    def __init__(self) -> None:
        self._message_queue = None

    def add_message_to_stream(self, message: ZeroMqMessage) -> None:
        self._ensure_queue().put_nowait(message)

    async def next_message(self) -> ZeroMqMessage:
        return await self._ensure_queue().get()

    def after_update(self) -> None:
        ...

    def _ensure_queue(self) -> asyncio.Queue:
        if self._message_queue is None:
            self._message_queue = asyncio.Queue()
        return self._message_queue
