import asyncio
import logging
from typing import Any

import aiozmq
import zmq

from tickit.core.adapter import Adapter, RaiseInterrupt
from tickit.core.device import Device

LOGGER = logging.getLogger(__name__)


class ZeroMQAdapter(Adapter):
    """An adapter for a ZeroMQ data stream."""

    zmq_host: str
    zmq_port: int
    running: bool

    _router: aiozmq.ZmqStream
    _dealer: aiozmq.ZmqStream

    def __init__(
        self, zmq_host: str = "127.0.0.1", zmq_port: int = 5555, running: bool = False
    ) -> None:
        """Initialize with default values."""
        super().__init__()
        self.zmq_host = zmq_host
        self.zmq_port = zmq_port
        self.running = running

    async def start_stream(self) -> None:
        """Start the ZeroMQ stream."""
        LOGGER.debug("Starting stream...")
        self._router = await aiozmq.create_zmq_stream(
            zmq.ROUTER, bind=f"tcp://{self.zmq_host}:{self.zmq_port}"
        )

        addr = list(self._router.transport.bindings())[0]
        self._dealer = await aiozmq.create_zmq_stream(zmq.DEALER, connect=addr)

        self._router.transport.setsockopt(zmq.LINGER, 0)
        self._dealer.transport.setsockopt(zmq.LINGER, 0)

    async def close_stream(self) -> None:
        """Close the ZeroMQ stream."""
        self._dealer.close()
        self._router.close()

        self.running = False

    def send_message(self, message: Any) -> None:
        """Send a message down the ZeroMQ stream.

        Sets up an asyncio task to put the message on the message queue, before
        being processed.

        Args:
            message (str): The message to send down the ZeroMQ stream.
        """
        asyncio.create_task(self._message_queue.put(message))

    async def run_forever(
        self, device: Device, raise_interrupt: RaiseInterrupt
    ) -> None:
        """Runs the ZeroMQ adapter continuously."""
        await super().run_forever(device, raise_interrupt)
        self._message_queue: asyncio.Queue = asyncio.Queue()
        await self.start_stream()
        self.running = True
        await self._process_message_queue()

    def check_if_running(self):
        """Returns the running state of the adapter."""
        return self.running

    async def _process_message_queue(self) -> None:
        running = True
        while running:
            message = await self._message_queue.get()
            await self._process_message(message)
            running = self.check_if_running()

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
