import sys
from typing import Awaitable, Callable, Tuple, TypeVar

from tickit.core.device import Device

# TODO: Investigate why import from tickit.utils.compat.typing_compat causes mypy error:
# >>> 54: error: Argument 1 to "handle" of "Interpreter" has incompatible type
#     "ComposedAdapter"; expected "Adapter"
# See mypy issue for details: https://github.com/python/mypy/issues/10851
if sys.version_info >= (3, 8):
    from typing import Protocol, runtime_checkable
else:
    from typing_extensions import Protocol, runtime_checkable

T = TypeVar("T")


@runtime_checkable
class Adapter(Protocol):
    async def run_forever(self) -> None:
        ...


@runtime_checkable
class Interpreter(Protocol[T]):
    async def handle(self, adapter: Adapter, message: T) -> Tuple[T, bool]:
        ...


@runtime_checkable
class Server(Protocol[T]):
    def __init__(self,) -> None:
        ...

    async def run_forever(self, handler: Callable[[T], Awaitable[T]]) -> None:
        ...


class ComposedAdapter:
    _interpreter: Interpreter
    _server: Server

    def __init__(
        self, device: Device, handle_interrupt: Callable[[], Awaitable[None]]
    ) -> None:
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
