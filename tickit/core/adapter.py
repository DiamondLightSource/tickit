import sys
from dataclasses import dataclass
from typing import Awaitable, Callable, Tuple, TypeVar

# TODO: Investigate why import from tickit.utils.compat.typing_compat causes mypy error:
# >>> 54: error: Argument 1 to "handle" of "Interpreter" has incompatible type
#     "ComposedAdapter"; expected "Adapter"
# See mypy issue for details: https://github.com/python/mypy/issues/10851
if sys.version_info >= (3, 8):
    from typing import Protocol, runtime_checkable
else:
    from typing_extensions import Protocol, runtime_checkable

T = TypeVar("T")


@dataclass
class AdapterConfig:
    adapter_class: str


@runtime_checkable
class Adapter(Protocol):
    async def run_forever(self) -> None:
        ...


@runtime_checkable
class Interpreter(Protocol[T]):
    async def handle(self, adapter: Adapter, message: T) -> Tuple[T, bool]:
        ...


@dataclass
class ServerConfig:
    server_class: str


@runtime_checkable
class Server(Protocol[T]):
    def __init__(self,) -> None:
        ...

    async def run_forever(self, handler: Callable[[T], Awaitable[T]]) -> None:
        ...
