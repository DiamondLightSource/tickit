from abc import abstractmethod
from inspect import getmembers
from typing import (
    AnyStr,
    AsyncIterable,
    Optional,
    Protocol,
    Sequence,
    Tuple,
    Union,
    runtime_checkable,
)

from tickit.core.adapter import Adapter


@runtime_checkable
class Command(Protocol):
    """An interface for interperable commands"""

    #: A flag which indicates whether calling of the method should trigger an interrupt
    interrupt: bool

    @abstractmethod
    def parse(self, data: bytes) -> Optional[Sequence[AnyStr]]:
        """An abstract method which parses a message and extracts arguments

        An abstract method which parses a message and produces arguments if a match is
        found, otherwise None is returned

        Args:
            data (bytes): The message to be parsed

        Returns:
            Optional[Sequence[AnyStr]]:
                A sequence of arguments extracted from the message if matched,
                otherwise None
        """
        pass


class CommandInterpreter:
    """An interpreter which routes to commands registered to adapter methods

    An interpreter which attempts to parse messages according to the parse method of
    commands registered against adapter methods, if a match is found the method is
    called with the parsed arguments.
    """

    @staticmethod
    async def _wrap(resp: AnyStr) -> AsyncIterable[AnyStr]:
        """An asynchronous method which converts singular replies to asynchronous iterables

        Args:
            resp (AnyStr): A singular reply message
        """

        yield resp

    @staticmethod
    async def unknown_command() -> AsyncIterable[bytes]:
        """An asynchronous iterable of length one used send an unknown command reply

        Returns:
            AsyncIterable[bytes]:
                An asynchronous iterable of length one containing the message "Request
                does not match any known command"
        """

        yield b"Request does not match any known command"

    async def handle(
        self, adapter: Adapter, message: bytes
    ) -> Tuple[AsyncIterable[Union[str, bytes]], bool]:
        """An asynchronous method which calls the matching command

        An asynchronous method which handles a message by attempting to match the
        message against each of the registered commands, if a match is found the
        corresponding command is called and its reply is returned with an asynchronous
        iterable wrapper if required. If no match is found the unknown command message
        is returned with no request for interrupt

        Args:
            adapter (Adapter): The adapter in which the function should be executed
            message (bytes): The message to be handled

        Returns:
            Tuple[AsyncIterable[Union[str, bytes]], bool]:
                A tuple of the asynchronous iterable of reply messages and a flag
                indicating whether an interrupt should be raised by the adapter
        """

        for _, method in getmembers(adapter):
            command = getattr(method, "__command__", None)
            if command is None:
                continue
            args = command.parse(message)
            if args is None:
                continue
            resp = await method(*args)
            if not isinstance(resp, AsyncIterable):
                resp = CommandInterpreter._wrap(resp)
            return resp, command.interrupt
        return CommandInterpreter.unknown_command(), False
