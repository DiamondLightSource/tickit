from dataclasses import dataclass
from typing import Awaitable, Callable, TypeVar

from tickit.core.adapter import Interpreter, Server, ServerConfig
from tickit.core.device import Device
from tickit.utils.dynamic_import import import_class

T = TypeVar("T")


@dataclass
class ComposedAdapterConfig:
    adapter_class: str
    server_config: ServerConfig


class ComposedAdapter:
    _interpreter: Interpreter
    _server: Server

    def __init__(
        self,
        device: Device,
        handle_interrupt: Callable[[], Awaitable[None]],
        composed_adapter_config: ComposedAdapterConfig,
    ) -> None:
        self._server = import_class(composed_adapter_config.server_config.server_class)(
            composed_adapter_config.server_config
        )
        assert isinstance(self._interpreter, Interpreter)
        assert isinstance(self._server, Server)
        self._device = device
        self.handle_interrupt = handle_interrupt

    async def run_forever(self) -> None:
        async def handle(message: T) -> T:
            reply, interrupt = await self._interpreter.handle(self, message)
            if interrupt:
                await self.handle_interrupt()
            return reply

        await self._server.run_forever(handle)
