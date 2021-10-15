import asyncio
import logging
from dataclasses import dataclass
from typing import AsyncIterable, Awaitable, Callable, List

import aiozmq
import zmq

from tickit.core.device import ConfigurableDevice

LOGGER = logging.getLogger(__name__)


@dataclass
class ZMQStream(ConfigurableDevice):
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


class ZeroMQAdapter:
    """An adapter for a ZeroMQ data stream."""

    _device: ZMQStream
    _raise_interrupt: Callable[[], Awaitable[None]]

    _dealer: zmq.DEALER
    _router: zmq.ROUTER

    def __init__(
        self,
        device: ZMQStream,
        raise_interrupt: Callable[[], Awaitable[None]],
        host: str = "localhost",
        port: int = 5555,
    ) -> None:
        """A CryostreamAdapter constructor which instantiates a TcpServer with host and port.

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

    async def start_stream(self) -> None:
        """[summary]."""
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
        tasks: List[asyncio.Task] = list()

        self.start_stream()

        async def handle(dealer: zmq.DEALER, router: zmq.ROUTER) -> None:
            async def reply(replies: AsyncIterable[int]) -> None:
                async for reply in replies:
                    if reply is None:
                        continue
                    LOGGER.debug("Replying with {!r}".format(reply))

                    for i in range(10):
                        msg = (b"data", b"ask", str(i).encode("utf-8"))
                        self._dealer.write(msg)
                        data = await self._router.read()
                        self._router.write(data)
                        answer = await self._dealer.read()
                        LOGGER.info("Received {!r}".format(answer))

            tasks.append(asyncio.create_task(reply(self.on_connect())))

        server = await asyncio.start_server(handle, self._host, self._port)

        async with server:
            await server.serve_forever()
