from dataclasses import dataclass
from typing import AsyncIterable, Generic, Optional, TypeVar

from tickit.core.adapter import Adapter, Interpreter, RaiseInterrupt, Server

#: Message type
T = TypeVar("T")

#: Device type
D = TypeVar("D")


@dataclass
class ComposedAdapter(Adapter[D], Generic[T, D]):
    """An adapter implementation which delegates to a server and interpreter.

    An adapter implementation which delegates the hosting of an external messaging
    protocol to a server and message handling to an interpreter.
    """

    server: Server
    interpreter: Interpreter

    async def on_connect(self) -> AsyncIterable[Optional[T]]:
        """Overridable asynchronous iterable which yields messages on client connection.

        Returns:
            AsyncIterable[Optional[T]]: An asynchronous iterable of messages.
        """
        if False:
            yield None

    async def handle_message(self, message: T) -> AsyncIterable[Optional[T]]:
        """Delegates message handling to the interpreter, raises interrupt if requested.

        Args:
            message (T): The message from the server to be handled.

        Returns:
            AsyncIterable[Optional[T]]: An asynchronous iterable of reply messages.
        """
        reply, interrupt = await self.interpreter.handle(self, message)
        if interrupt:
            await self.raise_interrupt()
        return reply

    async def run_forever(self, device: D, raise_interrupt: RaiseInterrupt) -> None:
        """Runs the server continuously."""
        await super().run_forever(device, raise_interrupt)
        await self.server.run_forever(self.on_connect, self.handle_message)
