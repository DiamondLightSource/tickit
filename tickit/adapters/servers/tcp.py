import asyncio
import logging
from asyncio.streams import StreamReader, StreamWriter
from typing import AsyncIterable, Awaitable, Callable, List

from tickit.core.adapter import ConfigurableServer
from tickit.utils.byte_format import ByteFormat

LOGGER = logging.getLogger(__name__)


class TcpServer(ConfigurableServer):
    """A configurable tcp server with delegated message handling for use in adapters"""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 25565,
        format: ByteFormat = ByteFormat(b"%b"),
    ) -> None:
        """A constructor for the tcp server

        Args:
            host (str): The host name which the server should be run under
            port (int): The port number which the server should listen to
            format (ByteFormat): A formatting string for messages sent by the server,
                allowing for the prepending and appending of data. Defaults to b"%b".
        """
        self.host = host
        self.port = port
        self.format = format

    async def run_forever(
        self,
        on_connect: Callable[[], AsyncIterable[bytes]],
        handler: Callable[[bytes], Awaitable[AsyncIterable[bytes]]],
    ) -> None:
        """An asynchronous method used to run the server indefinitely

        An asynchronous method used to run the server indefinitely on the configured
        host and port. Upon client connection, messages from the on_connect iterable
        will be sent. Upon recieving a message the server will delegate handling of it
        to the handler. Replies will be formatted according to the configured format
        string

        Args:
            on_connect (Callable[[], AsyncIterable[bytes]]): An asynchronous iterable
                of messages to be sent upon client connection
            handler (Callable[[bytes], Awaitable[AsyncIterable[bytes]]]): An
                asynchronous message handler which returns an asynchronous iterable of
                replies
        """
        tasks: List[asyncio.Task] = list()

        async def handle(reader: StreamReader, writer: StreamWriter) -> None:
            async def reply(replies: AsyncIterable[bytes]) -> None:
                async for reply in replies:
                    if reply is None:
                        continue
                    LOGGER.debug("Replying with {!r}".format(reply))
                    writer.write(self.format % reply)
                    if writer.is_closing():
                        break
                    await writer.drain()

            tasks.append(asyncio.create_task(reply(on_connect())))

            while True:
                data: bytes = await reader.read(1024)
                if data == b"":
                    break
                addr = writer.get_extra_info("peername")

                LOGGER.debug("Recieved {!r} from {}".format(data, addr))
                tasks.append(asyncio.create_task(reply(await handler(data))))

            await asyncio.wait(tasks)

        server = await asyncio.start_server(handle, self.host, self.port)

        async with server:
            await server.serve_forever()
