from abc import abstractmethod
from inspect import getmembers
from typing import (
    AnyStr,
    AsyncIterable,
    AsyncIterator,
    Optional,
    Protocol,
    Sequence,
    Tuple,
    get_type_hints,
    runtime_checkable,
)

from tickit.adapters.utils import wrap_as_async_iterator
from tickit.core.adapter import Interpreter, RaiseInterrupt
from tickit.utils.byte_format import ByteFormat


@runtime_checkable
class Command(Protocol):
    """An interface for interpretable commands."""

    #: A flag which indicates whether calling of the method should trigger an interrupt
    interrupt: bool

    @abstractmethod
    def parse(self, data: bytes) -> Optional[Sequence[AnyStr]]:
        """An abstract method which parses a message and extracts arguments.

        An abstract method which parses a message and produces arguments if a match is
        found, otherwise None is returned.

        Args:
            data (bytes): The message to be parsed.

        Returns:
            Optional[Sequence[AnyStr]]:
                A sequence of arguments extracted from the message if matched,
                otherwise None.
        """
        pass


class CommandAdapter(Interpreter[AnyStr]):
    """An adapter which routes to commands registered to adapter methods.

    An adapter which attempts to parse messages according to the parse method of
    commands registered against adapter methods, if a match is found the method is
    called with the parsed arguments.
    """

    _byte_format: ByteFormat = ByteFormat(b"%b")

    @property
    def byte_format(self) -> ByteFormat:
        return self._byte_format

    def after_update(self) -> None:
        ...

    async def handle_message(
        self,
        message: AnyStr,
        raise_interrupt: RaiseInterrupt,
    ) -> AsyncIterable[Optional[AnyStr]]:
        """Delegates message handling to the adapter, raises interrupt if requested.

        Args:
            message (T): The message from the server to be handled.

        Returns:
            AsyncIterable[Optional[T]]: An asynchronous iterable of reply messages.
        """
        reply, interrupt = await self.handle(message)
        if interrupt:
            await raise_interrupt()
        return reply

    async def handle(self, message: AnyStr) -> Tuple[AsyncIterator[AnyStr], bool]:
        """Matches the message to an adapter command and calls the corresponding method.

        An asynchronous method which handles a message by attempting to match the
        message against each of the registered commands, if a match is found the
        corresponding command is called and its reply is returned with an asynchronous
        iterator wrapper if required. If no match is found the unknown command message
        is returned with no request for interrupt.

        Args:
            adapter (Adapter): The adapter in which the function should be executed
            message (bytes): The message to be handled.

        Returns:
            Tuple[AsyncIterator[Union[str, bytes]], bool]:
                A tuple of the asynchronous iterator of reply messages and a flag
                indicating whether an interrupt should be raised by the adapter.
        """
        for _, method in getmembers(self):
            command = getattr(method, "__command__", None)
            if command is None:
                continue
            args = command.parse(message)
            if args is None:
                continue
            args = (
                argtype(arg)
                for arg, argtype in zip(args, get_type_hints(method).values())
            )
            resp = await method(*args)
            if not isinstance(resp, AsyncIterator):
                resp = wrap_as_async_iterator(resp)
            return resp, command.interrupt

        msg = "Request does not match any known command"
        # This is a pain but the message needs to match the input message
        # TODO: Fix command interpreters' handling of bytes vs str
        if isinstance(message, bytes):
            resp = wrap_as_async_iterator(msg.encode("utf-8"))
            return resp, False
        else:
            resp = wrap_as_async_iterator(msg)
            return resp, False

    async def on_connect(self) -> AsyncIterable[Optional[AnyStr]]:
        """Overridable asynchronous iterable which yields messages on client connection.

        Returns:
            AsyncIterable[Optional[T]]: An asynchronous iterable of messages.
        """
        if False:
            yield None
