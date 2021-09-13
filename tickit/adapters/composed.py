from dataclasses import dataclass
from typing import AsyncIterable, Awaitable, Callable, Optional, TypeVar

from tickit.core.adapter import Interpreter, Server
from tickit.core.device import Device

T = TypeVar("T")


@dataclass
class ComposedAdapter:
    _device: Device
    _raise_interrupt: Callable[[], Awaitable[None]]
    _server: Server
    _interpreter: Interpreter

    async def on_connect(self) -> AsyncIterable[Optional[T]]:
        if False:
            yield None

    async def handle_message(self, message: T) -> AsyncIterable[Optional[T]]:
        reply, interrupt = await self._interpreter.handle(self, message)
        if interrupt:
            await self._raise_interrupt()
        return reply

    async def run_forever(self) -> None:
        await self._server.run_forever(self.on_connect, self.handle_message)
