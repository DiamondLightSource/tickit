from typing import AsyncIterable, Awaitable, Callable, Optional, TypeVar

from tickit.core.adapter import ConfigurableAdapter, Interpreter, Server, ServerConfig
from tickit.core.device import Device

T = TypeVar("T")


class ComposedAdapter(ConfigurableAdapter):
    _interpreter: Interpreter
    _server: Server

    def __init__(
        self,
        device: Device,
        handle_interrupt: Callable[[], Awaitable[None]],
        server_config: ServerConfig,
    ) -> None:
        self._server = server_config.configures()(**server_config.__kwargs__)
        assert isinstance(self._interpreter, Interpreter)
        assert isinstance(self._server, Server)
        self._device = device
        self.handle_interrupt = handle_interrupt

    async def on_connect(self) -> AsyncIterable[Optional[T]]:
        if False:
            yield None

    async def handle_message(self, message: T) -> AsyncIterable[Optional[T]]:
        reply, interrupt = await self._interpreter.handle(self, message)
        if interrupt:
            await self.handle_interrupt()
        return reply

    async def run_forever(self) -> None:
        await self._server.run_forever(self.on_connect, self.handle_message)
