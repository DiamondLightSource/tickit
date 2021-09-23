from dataclasses import dataclass
from typing import AsyncIterable, Awaitable, Callable, Optional, TypeVar

from tickit.core.adapter import Interpreter, Server
from tickit.core.device import Device

#: Message type
T = TypeVar("T")


@dataclass
class ComposedAdapter:
    """An adapter implementation which delegates to a server and interpreter.

    An adapter implementation which delegates the hosting of an external messaging
    protocol to a server and message handling to an interpreter.
    """

    _device: Device
    _raise_interrupt: Callable[[], Awaitable[None]]
    _server: Server
    _interpreter: Interpreter

    async def on_connect(self) -> AsyncIterable[Optional[T]]:
        """An overridable asynchronous iterable which yields messages on client connection.

        Returns:
            AsyncIterable[Optional[T]]: An asynchronous iterable of messages.
        """
        if False:
            yield None

    async def handle_message(self, message: T) -> AsyncIterable[Optional[T]]:
        """Delegates message handling to the interpreter and raises interrupt if requested.

        Args:
            message (T): The message from the server to be handled.

        Returns:
            AsyncIterable[Optional[T]]: An asynchronous iterable of reply messages.
        """
        reply, interrupt = await self._interpreter.handle(self, message)
        if interrupt:
            await self._raise_interrupt()
        return reply

    async def run_forever(self) -> None:
        """Runs the server continously."""
        await self._server.run_forever(self.on_connect, self.handle_message)
