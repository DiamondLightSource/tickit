from abc import ABC, abstractmethod
from typing import AsyncIterable, Generic, Tuple, TypeVar

from typing_extensions import Protocol

#: Message type
T = TypeVar("T")


class RaiseInterrupt(Protocol):
    """A raise_interrupt function that should be passed the adapter."""

    async def __call__(self) -> None:
        """The actual call signature."""
        pass


A = TypeVar("A")


class AdapterIo(ABC, Generic[A]):
    """Io logic with a setup method for an adapter object."""

    @abstractmethod
    async def setup(self, adapter: A, raise_interrupt: RaiseInterrupt) -> None:
        ...


class AdapterContainer(Generic[A]):
    """A container for an object specific adapter and the required functional io."""

    adapter: A
    io: AdapterIo[A]

    def __init__(self, adapter: A, io: AdapterIo) -> None:
        self.adapter = adapter
        self.io = io

    async def run_forever(self, raise_interrupt: RaiseInterrupt) -> None:
        """An asynchronous method allowing indefinite running of core adapter logic.

        An asynchronous method allowing for indefinite running of core adapter logic
        (typically the hosting of a protocol server and the interpretation of commands
        which are supplied via it).
        """

        await self.io.setup(self.adapter, raise_interrupt)


class Interpreter(ABC, Generic[T]):
    """An interface for types which handle messages received by an adapter."""

    @abstractmethod
    async def handle(self, message: T) -> Tuple[AsyncIterable[T], bool]:
        """An asynchronous method which handles messages received by an adapter.

        An asynchronous method which handles messages received by an adapter, replies
        are sent as an asynchronous iterable to support setting of continuous readback,
        stand alone replies should be wrapped in an asynchronous iterable of length one.

        Args:
            adapter (Adapter): The adapter which is delegating message handling.
            message (T): The message received by the adapter.

        Returns:
            Tuple[AsyncIterable[T], bool]: A tuple containing both an asynchronous
                iterable of reply messages and an interrupt flag.
        """
