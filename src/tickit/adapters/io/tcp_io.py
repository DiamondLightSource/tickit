import asyncio
import logging
from asyncio.streams import StreamReader, StreamWriter
from typing import AsyncIterable, Awaitable, Callable, List, Optional

from tickit.adapters.tcp import CommandAdapter
from tickit.core.adapter import AdapterIo, RaiseInterrupt
from tickit.utils.byte_format import ByteFormat

LOGGER = logging.getLogger(__name__)


class TcpIo(AdapterIo[CommandAdapter]):
    """An AdapterIo implementation which delegates to a tcp server.

    An AdapterIo implementation which delegates the hosting of an external messaging
    protocol to a server and utilises message handling from a CommandAdapter.
    """

    host: str
    port: int

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port

    async def setup(
        self, adapter: CommandAdapter, raise_interrupt: RaiseInterrupt
    ) -> None:
        handle = self._generate_handle_function(
            adapter.on_connect,
            adapter.handle_message,
            raise_interrupt,
            adapter.byte_format,
        )

        server = await asyncio.start_server(handle, self.host, self.port)

        async def run_forever() -> None:
            async with server:
                await server.serve_forever()

        asyncio.create_task(run_forever())

    def _generate_handle_function(
        self,
        on_connect: Callable[[], AsyncIterable[Optional[bytes]]],
        handler: Callable[
            [bytes, RaiseInterrupt], Awaitable[AsyncIterable[Optional[bytes]]]
        ],
        raise_interrupt: RaiseInterrupt,
        format: ByteFormat,
    ) -> Callable[[StreamReader, StreamWriter], Awaitable[None]]:
        """Generates the handle function to be passed to the server.

        The handle function is generated from the specified functions. Its purpose is
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
                    LOGGER.debug(f"Replying with {reply!r}")
                    writer.write(format.format % reply)
                    if writer.is_closing():
                        break
                    await writer.drain()

            tasks.append(asyncio.create_task(reply(on_connect())))

            while True:
                data: bytes = await reader.read(1024)
                if data == b"":
                    break
                addr = writer.get_extra_info("peername")

                LOGGER.debug(f"Received {data!r} from {addr}")
                tasks.append(
                    asyncio.create_task(
                        reply(
                            await handler(
                                data,
                                raise_interrupt,
                            )
                        )
                    )
                )

            await asyncio.wait(tasks)

        return handle
