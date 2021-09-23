import sys
from typing import (
    TYPE_CHECKING,
    AsyncIterable,
    Awaitable,
    Callable,
    Optional,
    Tuple,
    TypeVar,
)

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

#: Message type
T = TypeVar("T")


# https://github.com/python/mypy/issues/708#issuecomment-647124281
class RaiseInterrupt(Protocol):
    """A raise_interrupt function that should be passed to `Adapter`."""

    async def __call__(self) -> None:
        """The actual call signature."""
        pass


@runtime_checkable
class Adapter(Protocol):
    """An interface for types which implement device adapters."""

    device: "Device"
    raise_interrupt: RaiseInterrupt

    async def run_forever(self) -> None:
        """An asynchronous method allowing indefinite running of core adapter logic.

        An asynchronous method allowing for indefinite running of core adapter logic
        (typically the hosting of a protocol server and the interpretation of commands
        which are supplied via it).
        """
        pass


@runtime_checkable
class ListeningAdapter(Adapter, Protocol):
    """An interface for adapters which require to be notified after a device updates."""

    def after_update(self):
        """A method which is called immediately after the device updates."""
        pass


@runtime_checkable
class Interpreter(Protocol[T]):
    """An interface for types which handle messages recieved by an adapter."""

    async def handle(
        self, adapter: Adapter, message: T
    ) -> Tuple[AsyncIterable[T], bool]:
        """An asynchronous method which handles messages recieved by an adapter.

        An asynchronous method which handles messages recieved by an adapter, replies
        are sent as an asynchronous iterable to support setting of continious readback,
        stand alone replies should be wrapped in an asynchronous iterable of length one.

        Args:
            adapter (Adapter): The adapter which is delegating message handling.
            message (T): The message recieved by the adapter.

        Returns:
            Tuple[AsyncIterable[T], bool]: A tuple containing both an asynchronous
                iterable of reply messages and an interrupt flag.
        """
        pass


@runtime_checkable
class Server(Protocol[T]):
    """An interface for types which implement an external messaging protocol."""

    def __init__(self, **kwargs) -> None:
        """A Server constructor which may recieve key word arguments."""
        pass

    async def run_forever(
        self,
        on_connect: Callable[[], AsyncIterable[Optional[T]]],
        handler: Callable[[T], Awaitable[AsyncIterable[Optional[T]]]],
    ) -> None:
        """An asynchronous method allowing indefinite running of core server logic.

        Args:
            on_connect (Callable[[], AsyncIterable[Optional[T]]]): An asynchronous
                iterable of messages to be sent once a client connects.
            handler (Callable[[T], Awaitable[AsyncIterable[Optional[T]]]]): An
                asynchronous method used to handle recieved messages, returning an
                asynchronous iterable of replies.
        """
        pass
