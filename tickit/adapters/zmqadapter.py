import asyncio
import logging
from dataclasses import dataclass
from typing import Any

import aiozmq
import zmq

from tickit.core.adapter import Adapter, RaiseInterrupt
from tickit.core.device import Device

LOGGER = logging.getLogger(__name__)


@dataclass
class ZeroMQAdapter(Adapter):
    """An adapter for a ZeroMQ data stream."""

    zmq_host: str = "127.0.0.1"
    zmq_port: int = 5555

    async def start_stream(self) -> None:
        """[summary]."""
        LOGGER.debug("Starting stream...")
        self._router = await aiozmq.create_zmq_stream(
            zmq.ROUTER, bind=f"tcp://{self.zmq_host}:{self.zmq_port}"
        )

        addr = list(self._router.transport.bindings())[0]
        self._dealer = await aiozmq.create_zmq_stream(zmq.DEALER, connect=addr)

    async def close_stream(self) -> None:
        """[summary]."""
        self._dealer.close()
        self._router.close()

    def send_message(self, message: Any) -> None:
        """[summary].

        Args:
            message (Any): [description]
        """
        asyncio.create_task(self._message_queue.put(message))

    async def run_forever(
        self, device: Device, raise_interrupt: RaiseInterrupt
    ) -> None:
        """[summary].

        Yields:
            [type]: [description]
        """
        await super().run_forever(device, raise_interrupt)
        self._message_queue: asyncio.Queue = asyncio.Queue()
        await self.start_stream()
        await self._process_message_queue()

    async def _process_message_queue(self) -> None:
        while True:
            message = await self._message_queue.get()
            await self._process_message(message)

    async def _process_message(self, message: str) -> None:
        if message is not None:
            LOGGER.debug("Data from ZMQ stream: {!r}".format(message))

            msg = (b"Data", str(message).encode("utf-8"))
            self._dealer.write(msg)
            data = await self._router.read()
            self._router.write(data)
            answer = await self._dealer.read()
            LOGGER.debug("Received {!r}".format(answer))
        else:
            LOGGER.debug("No message")
