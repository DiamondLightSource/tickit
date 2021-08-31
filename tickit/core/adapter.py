import sys
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    AsyncIterable,
    Awaitable,
    Callable,
    Dict,
    Optional,
    Tuple,
    Type,
    TypeVar,
)

from tickit.utils.configuration.configurable import configurable, configurable_base

# TODO: Investigate why import from tickit.utils.compat.typing_compat causes mypy error:
# >>> 54: error: Argument 1 to "handle" of "Interpreter" has incompatible type
#     "ComposedAdapter"; expected "Adapter"
# See mypy issue for details: https://github.com/python/mypy/issues/10851
if sys.version_info >= (3, 8):
    from typing import Protocol, runtime_checkable
elif sys.version_info >= (3, 5):
    from typing_extensions import Protocol, runtime_checkable

if TYPE_CHECKING:
    from tickit.core.device import Device

T = TypeVar("T")


@runtime_checkable
class Adapter(Protocol):
    def __init__(
        self, device: "Device", raise_interrupt: Callable[[], Awaitable[None]], **kwargs
    ) -> None:
        pass

    async def run_forever(self) -> None:
        pass


@runtime_checkable
class ListeningAdapter(Adapter, Protocol):
    def after_update(self):
        pass


@configurable_base
@dataclass
class AdapterConfig:
    @staticmethod
    def configures() -> Type[Adapter]:
        raise NotImplementedError

    @property
    def kwargs(self) -> Dict[str, object]:
        raise NotImplementedError


class ConfigurableAdapter:
    def __init_subclass__(cls) -> None:
        cls = configurable(AdapterConfig, ["device", "raise_interrupt"])(cls)


@runtime_checkable
class Interpreter(Protocol[T]):
    async def handle(
        self, adapter: Adapter, message: T
    ) -> Tuple[AsyncIterable[T], bool]:
        pass


@runtime_checkable
class Server(Protocol[T]):
    def __init__(self, **kwargs) -> None:
        pass

    async def run_forever(
        self,
        on_connect: Callable[[], AsyncIterable[Optional[T]]],
        handler: Callable[[T], Awaitable[AsyncIterable[Optional[T]]]],
    ) -> None:
        pass


@configurable_base
@dataclass
class ServerConfig:
    @staticmethod
    def configures() -> Type[Server]:
        raise NotImplementedError

    @property
    def kwargs(self):
        raise NotImplementedError


class ConfigurableServer:
    def __init_subclass__(cls) -> None:
        cls = configurable(ServerConfig)(cls)
