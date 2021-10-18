import asyncio
import logging
from dataclasses import dataclass
from typing import AsyncIterable, Awaitable, Callable, List

import aiozmq
import zmq

from tickit.core.adapter import ConfigurableAdapter
from tickit.core.device import ConfigurableDevice

LOGGER = logging.getLogger(__name__)


@dataclass
class ZeroMQStream(ConfigurableDevice):
    """A ZeroMQ data stream."""

    async def update(self) -> AsyncIterable[int]:
        """A method which continiously yields an int.

        Returns:
            AsyncIterable[int]: An asyncronous iterable of ints.
        """
        i = 0
        while True:
            yield i
            i += 1
            await asyncio.sleep(1.0)


class ZeroMQAdapter(ConfigurableAdapter):
    """An adapter for a ZeroMQ data stream."""

    _device: ZeroMQStream
    _raise_interrupt: Callable[[], Awaitable[None]]

    _dealer: zmq.DEALER
    _router: zmq.ROUTER

    def __init__(
        self,
        device: ZeroMQStream,
        raise_interrupt: Callable[[], Awaitable[None]],
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
        self._device = device
        self._host = host
        self._port = port
        self.tasks: List[asyncio.Task] = list()

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

    async def on_connect(self) -> AsyncIterable[int]:
        """A method which continiously yields stream packets.

        Returns:
            AsyncIterable[bytes]: An asyncronous iterable of stream packets.
        """
        while True:
            await asyncio.sleep(2.0)
            async for i in self._device.update():
                yield i

    async def run_forever(self) -> None:
        """[summary].

        Yields:
            [type]: [description]
        """
        await self.start_stream()

        async def reply(replies: AsyncIterable[int]) -> None:
            async for reply in replies:
                if reply is None:
                    LOGGER.debug("No reply...")
                    continue
                LOGGER.debug("Data from ZMQ stream: {!r}".format(reply))

                msg = (b"Data", str(reply).encode("utf-8"))
                self._dealer.write(msg)
                data = await self._router.read()
                self._router.write(data)
                answer = await self._dealer.read()
                LOGGER.info("Received {!r}".format(answer))

        self.tasks.append(asyncio.create_task(reply(self.on_connect())))

        await asyncio.wait(self.tasks)
