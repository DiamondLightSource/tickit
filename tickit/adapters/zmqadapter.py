import asyncio
from dataclasses import dataclass
from typing import AsyncIterable, Awaitable, Callable

import aiozmq
import zmq

from tickit.adapters.servers.tcp import TcpServer
from tickit.utils.byte_format import ByteFormat


@dataclass
class ZMQStream:
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

    _stream: ZMQStream
    _raise_interrupt: Callable[[], Awaitable[None]]
    _server: TcpServer

    _dealer: zmq.DEALER
    _router: zmq.ROUTER

    def __init__(
        self,
        stream: ZMQStream,
        raise_interrupt: Callable[[], Awaitable[None]],
        host: str = "localhost",
        port: int = 5555,
    ) -> None:
        """A CryostreamAdapter constructor which instantiates a TcpServer with host and port.

        Args:
            stream (ZMQStream): The ZMQ stream which this adapter is attached to
            raise_interrupt (Callable): A callback to request that the device is
                updated immediately.
            host (Optional[str]): The host address of the TcpServer. Defaults to
                "localhost".
            port (Optional[int]): The bound port of the TcpServer. Defaults to 5555.
        """
        self._stream = stream
        self._server = TcpServer(host, port, ByteFormat(b"%b\r\n"))

    async def run_forever(self) -> None:
        """[summary].

        Yields:
            [type]: [description]
        """
        self._router = await aiozmq.create_zmq_stream(
            zmq.ROUTER, bind="tcp://127.0.0.1:*"
        )

        addr = list(self._router.transport.bindings())[0]
        self._dealer = await aiozmq.create_zmq_stream(zmq.DEALER, connect=addr)

        for i in range(10):
            msg = (b"data", b"ask", str(i).encode("utf-8"))
            self._dealer.write(msg)
            data = await self._router.read()
            self._router.write(data)
            answer = await self._dealer.read()
            print(answer)
        self._dealer.close()
        self._router.close()
