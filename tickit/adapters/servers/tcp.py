import asyncio
import logging
from asyncio.streams import StreamReader, StreamWriter
from typing import AsyncIterable, Awaitable, Callable, List, Optional

from tickit.core.adapter import Server
from tickit.utils.byte_format import ByteFormat

LOGGER = logging.getLogger(__name__)


class TcpServer(Server[bytes]):
    """A configurable tcp server with delegated message handling for use in adapters."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 25565,
        format: ByteFormat = ByteFormat(b"%b"),
    ) -> None:
        """The TcpServer constructor which takes a host, port and format byte string.

        Args:
            host (str): The host name which the server should be run under.
            port (int): The port number which the server should listen to.
            format (ByteFormat): A formatting string for messages sent by the server,
                allowing for the prepending and appending of data. Defaults to b"%b".
        """
        self.host = host
        self.port = port
        self.format = format.format

    async def run_forever(
        self,
        on_connect: Callable[[], AsyncIterable[Optional[bytes]]],
        handler: Callable[[bytes], Awaitable[AsyncIterable[Optional[bytes]]]],
    ) -> None:
        """Runs the TCP server indefinitely on the configured host and port.

        An asynchronous method used to run the server indefinitely on the configured
        host and port. Upon client connection, messages from the on_connect iterable
        will be sent. Upon recieving a message the server will delegate handling of it
        to the handler. Replies will be formatted according to the configured format
        string.

        Args:
            on_connect (Callable[[], AsyncIterable[bytes]]): An asynchronous iterable
                of messages to be sent upon client connection.
            handler (Callable[[bytes], Awaitable[AsyncIterable[bytes]]]): An
                asynchronous message handler which returns an asynchronous iterable of
                replies.
        """
        handle = self._generate_handle_function(on_connect, handler)

        server = await asyncio.start_server(handle, self.host, self.port)

        async with server:
            await server.serve_forever()

    def _generate_handle_function(
        self,
        on_connect: Callable[[], AsyncIterable[Optional[bytes]]],
        handler: Callable[[bytes], Awaitable[AsyncIterable[Optional[bytes]]]],
    ) -> Callable[[StreamReader, StreamWriter], Awaitable[None]]:
        """Generates the handle function to be passed to the server.

        The handle function is generated from the specified functions. It's purpose is
        to define how the server will respond to incoming messages.

        Args:
            on_connect (Callable[[], AsyncIterable[bytes]]): An asynchronous iterable
                of messages to be sent upon client connection.
            handler (Callable[[bytes], Awaitable[AsyncIterable[bytes]]]): An
                asynchronous message handler which returns an asynchronous iterable of
                replies.
        """
        tasks: List[asyncio.Task] = list()

        async def handle(reader: StreamReader, writer: StreamWriter) -> None:
            async def reply(replies: AsyncIterable[Optional[bytes]]) -> None:
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

        return handle
