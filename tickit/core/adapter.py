from typing import (
    Any,
    AsyncIterable,
    Awaitable,
    Callable,
    Generic,
    Optional,
    Tuple,
    TypeVar,
)

from typing_extensions import Protocol

from tickit.core.device import Device
from tickit.utils.configuration.configurable import as_tagged_union

#: Message type
T = TypeVar("T")


# https://github.com/python/mypy/issues/708#issuecomment-647124281
class RaiseInterrupt(Protocol):
    """A raise_interrupt function that should be passed to `Adapter`."""

    async def __call__(self) -> None:
        """The actual call signature."""
        pass


@as_tagged_union
class Adapter:
    """An interface for types which implement device adapters."""

    device: Device
    raise_interrupt: RaiseInterrupt

    def __getattr__(self, name: str) -> Any:
        """Improve error message for getting attributes before `run_forever`."""
        if name in ("device", "raise_interrupt"):
            raise RuntimeError(
                "Can't get self.device or self.raise_interrupt before run_forever()"
            )
        return super().__getattribute__(name)

    async def run_forever(
        self, device: Device, raise_interrupt: RaiseInterrupt
    ) -> None:
        """An asynchronous method allowing indefinite running of core adapter logic.

        An asynchronous method allowing for indefinite running of core adapter logic
        (typically the hosting of a protocol server and the interpretation of commands
        which are supplied via it).
        """
        self.device = device
        self.raise_interrupt = raise_interrupt

    def after_update(self):
        """A method which is called immediately after the device updates."""


@as_tagged_union
class Interpreter(Generic[T]):
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


@as_tagged_union
class Server(Generic[T]):
    """An interface for types which implement an external messaging protocol."""

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
