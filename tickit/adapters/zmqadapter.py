import asyncio
import logging
from typing import Any

import aiozmq
import zmq

from tickit.core.adapter import Adapter
from tickit.core.device import Device

LOGGER = logging.getLogger(__name__)


class ZeroMQAdapter(Adapter):
    """An adapter for a ZeroMQ data stream."""

    device: Device

    _dealer: zmq.DEALER
    _router: zmq.ROUTER
    _message_queue: asyncio.Queue

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 5555,
    ) -> None:
        """A ZeroMQAdapter constructor which instantiates a TcpServer with host and port.

        Args:
            device (ZMQStream): The ZMQ stream/device which this adapter is attached to
            raise_interrupt (Callable): A callback to request that the device is
                updated immediately.
            host (Optional[str]): The host address of the TcpServer. Defaults to
                "localhost".
            port (Optional[int]): The bound port of the TcpServer. Defaults to 5555.
        """
        # self._raise_interrupt = raise_interrupt
        self._host = host
        self._port = port

    async def start_stream(self) -> None:
        """[summary]."""
        LOGGER.debug("Starting stream...")
        self._router = await aiozmq.create_zmq_stream(
            zmq.ROUTER, bind=f"tcp://{self._host}:{self._port}"
        )

        addr = list(self._router.transport.bindings())[0]
        self._dealer = await aiozmq.create_zmq_stream(zmq.DEALER, connect=addr)

    async def close_stream(self) -> None:
        """[summary]."""
        self._dealer.close()
        self._router.close()

    async def send_message(self, message: Any) -> None:
        """[summary].

        Args:
            message (Any): [description]
        """
        await self._message_queue.put(message)

    async def run_forever(self, device, raise_interrupt) -> None:
        """[summary].

        Yields:
            [type]: [description]
        """
        await super().run_forever(device, raise_interrupt)
        self._message_queue = asyncio.Queue()
        await self.start_stream()
        await self._process_message_queue()

    async def _process_message_queue(self) -> None:
        while True:
            message = await self._message_queue.get()
            if message is not None:
                LOGGER.debug("Data from ZMQ stream: {!r}".format(message))

                msg = (b"Data", str(message).encode("utf-8"))
                self._dealer.write(msg)
                data = await self._router.read()
                self._router.write(data)
                answer = await self._dealer.read()
                LOGGER.info("Received {!r}".format(answer))
            else:
                LOGGER.debug("No message")
