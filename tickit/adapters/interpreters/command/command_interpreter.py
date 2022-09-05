from abc import abstractmethod
from inspect import getmembers
from typing import (
    AnyStr,
    AsyncIterable,
    Optional,
    Sequence,
    Tuple,
    cast,
    get_type_hints,
)

from tickit.core.adapter import Adapter, Interpreter
from tickit.utils.compat.typing_compat import Protocol, runtime_checkable


@runtime_checkable
class Command(Protocol):
    """An interface for interperable commands."""

    #: A flag which indicates whether calling of the method should trigger an interrupt
    interrupt: bool
    # format: Optional[str] = None

    @abstractmethod
    def parse(self, data: AnyStr) -> Optional[Tuple[Sequence[AnyStr], int, int, int]]:
        """An abstract method which parses a message and extracts arguments.

        An abstract method which parses a message and produces arguments if a match is
        found, otherwise None is returned.

        Args:
            data (AnyStr): The message to be parsed.

        Returns:
            Optional[Sequence[AnyStr]]:
                A sequence of arguments extracted from the message if matched,
                otherwise None.
        """
        pass


class CommandInterpreter(Interpreter[AnyStr]):
    """An interpreter which routes to commands registered to adapter methods.

    An interpreter which attempts to parse messages according to the parse method of
    commands registered against adapter methods, if a match is found the method is
    called with the parsed arguments.
    """

    @staticmethod
    async def _wrap(reply: AnyStr) -> AsyncIterable[AnyStr]:
        """Wraps the reply in an asynchronous iterable.

        Args:
            response (AnyStr): A singular reply message.

        Returns:
            AsyncIterable[AnyStr]: An asynchronous iterable containing the reply
                message.
        """
        yield reply

    @staticmethod
    async def unknown_command() -> AsyncIterable[bytes]:
        """An asynchronous iterable of containing a single unknown command reply.

        Returns:
            AsyncIterable[bytes]:
                An asynchronous iterable of containing a single unknown command reply:
                "Request does not match any known command".
        """
        yield b"Request does not match any known command"

    async def handle(
        self, adapter: Adapter, message: AnyStr
    ) -> Tuple[AsyncIterable[AnyStr], bool]:
        """Matches the message to an adapter command and calls the corresponding method.

        An asynchronous method which handles a message by attempting to match the
        message against each of the registered commands, if a match is found the
        corresponding command is called and its reply is returned with an asynchronous
        iterable wrapper if required. If no match is found the unknown command message
        is returned with no request for interrupt.

        Args:
            adapter (Adapter): The adapter in which the function should be executed
            message (bytes): The message to be handled.

        Returns:
            Tuple[AsyncIterable[Union[str, bytes]], bool]:
                A tuple of the asynchronous iterable of reply messages and a flag
                indicating whether an interrupt should be raised by the adapter.
        """
        for _, method in getmembers(adapter):
            message = message
            command = cast(Command, getattr(method, "__command__", None))
            if command is None:
                continue
            parse_result = command.parse(message)
            if parse_result is None:
                continue
            (
                match_groups,
                _,
                match_end,
                message_end,
            ) = parse_result
            if match_end != message_end:
                # We want the whole (formatted) message to match a command
                continue
            args = (
                argtype(arg)
                for arg, argtype in zip(match_groups, get_type_hints(method).values())
            )
            # can we use signature instead to more cleverly do conversions? i.e. if
            # type hints aren't available just pass on with no conversion? Otherwise
            # we can get unhelpful error messages.
            # Also, should we deal with str/bytes conversions seperately?
            # Create a mapping function that does conversion rather than argtype(arg)?
            # It would take args and inspect.Parameters as parameters?
            # Is type hints enough? - doesn't know about non-hinted vars
            resp = await method(*args)
            if not isinstance(resp, AsyncIterable):
                resp = CommandInterpreter._wrap(resp)
            return resp, command.interrupt
        resp = CommandInterpreter.unknown_command()
        return resp, False
