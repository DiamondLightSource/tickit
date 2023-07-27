import asyncio
import logging
from asyncio.streams import StreamReader, StreamWriter
from inspect import getmembers
from typing import (
    AnyStr,
    AsyncIterable,
    AsyncIterator,
    Awaitable,
    Callable,
    List,
    Optional,
    Tuple,
    get_type_hints,
)

from tickit.adapters.interpreters.utils import wrap_as_async_iterator
from tickit.core.adapter import AdapterIo, RaiseInterrupt
from tickit.utils.byte_format import ByteFormat

LOGGER = logging.getLogger(__name__)


class TcpAdapter:
    """But actually this is the interpereter.

    An interpreter which routes to commands registered to adapter methods.

    An interpreter which attempts to parse messages according to the parse method of
    commands registered against adapter methods, if a match is found the method is
    called with the parsed arguments.
    """

    _byte_format: ByteFormat = ByteFormat(b"%b")

    @property
    def byte_format(self) -> ByteFormat:
        return self._byte_format

    def after_update(self) -> None:
        ...

    async def handle_message(
        self,
        message: AnyStr,
        raise_interrupt: RaiseInterrupt,
    ) -> AsyncIterable[Optional[AnyStr]]:
        """Delegates message handling to the interpreter, raises interrupt if requested.

        Args:
            message (T): The message from the server to be handled.

        Returns:
            AsyncIterable[Optional[T]]: An asynchronous iterable of reply messages.
        """
        reply, interrupt = await self.handle(message)
        if interrupt:
            await raise_interrupt()
        return reply

    async def handle(self, message: AnyStr) -> Tuple[AsyncIterator[AnyStr], bool]:
        """Matches the message to an adapter command and calls the corresponding method.

        An asynchronous method which handles a message by attempting to match the
        message against each of the registered commands, if a match is found the
        corresponding command is called and its reply is returned with an asynchronous
        iterator wrapper if required. If no match is found the unknown command message
        is returned with no request for interrupt.

        Args:
            adapter (Adapter): The adapter in which the function should be executed
            message (bytes): The message to be handled.

        Returns:
            Tuple[AsyncIterator[Union[str, bytes]], bool]:
                A tuple of the asynchronous iterator of reply messages and a flag
                indicating whether an interrupt should be raised by the adapter.
        """
        for _, method in getmembers(self):
            command = getattr(method, "__command__", None)
            if command is None:
                continue
            args = command.parse(message)
            if args is None:
                continue
            args = (
                argtype(arg)
                for arg, argtype in zip(args, get_type_hints(method).values())
            )
            resp = await method(*args)
            if not isinstance(resp, AsyncIterator):
                resp = wrap_as_async_iterator(resp)
            return resp, command.interrupt

        msg = "Request does not match any known command"
        # This is a pain but the message needs to match the input message
        # TODO: Fix command interpreters' handling of bytes vs str
        if isinstance(message, bytes):
            resp = wrap_as_async_iterator(msg.encode("utf-8"))
            return resp, False
        else:
            resp = wrap_as_async_iterator(msg)
            return resp, False

    async def on_connect(self) -> AsyncIterable[Optional[AnyStr]]:
        """Overridable asynchronous iterable which yields messages on client connection.

        Returns:
            AsyncIterable[Optional[T]]: An asynchronous iterable of messages.
        """
        if False:
            yield None


class TcpIo(AdapterIo[TcpAdapter]):
    host: str
    port: int

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port

    async def setup(self, adapter: TcpAdapter, raise_interrupt: RaiseInterrupt) -> None:
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
