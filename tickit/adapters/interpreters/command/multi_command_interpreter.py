from inspect import getmembers
from typing import (
    AnyStr,
    AsyncIterable,
    Callable,
    List,
    NamedTuple,
    Optional,
    Sequence,
    Tuple,
    cast,
    get_type_hints,
)

from tickit.adapters.interpreters.command.command_interpreter import Command
from tickit.adapters.interpreters.utils import wrap_messages_as_async_iterable
from tickit.core.adapter import Adapter, Interpreter


class MultiCommandInterpreter(Interpreter[AnyStr]):
    """An interpreter which routes to commands registered to adapter methods.

    An interpreter which attempts to parse commands from within a message. Matching
    adapter methods are called with the parsed arguments.
    """

    def __init__(self, ignore_whitespace=True) -> None:
        """An interpreter which routes to commands registered to adapter methods.

        An interpreter which attempts to parse commands from within a message. Matching
        adapter methods are called with the parsed arguments.

        Args:
            ignore_whitespace (bool): A boolean flag indicating whether whitesace
                should be ignored when parsing commands from within a message.
        """
        super().__init__()
        self.ignore_whitespace = ignore_whitespace

    @staticmethod
    def _convert_args_to_method_types(arg_strings: Sequence[AnyStr], method: Callable):
        args = (
            argtype(arg)
            for arg, argtype in zip(arg_strings, get_type_hints(method).values())
        )
        return args

    @staticmethod
    async def unknown_command() -> AsyncIterable[AnyStr]:
        """An asynchronous iterable of containing a single unknown command reply.

        Returns:
            AsyncIterable[bytes]:
                An asynchronous iterable of containing a single unknown command reply:
                "Request does not match any known command".
        """
        yield cast(AnyStr, b"Request does not match any known command")

    class MatchInfo(NamedTuple):
        """NamedTuple wrapper for information about a command that matches a message."""

        match_length: int
        command: Command
        command_method: Callable
        command_args: Sequence

    def _get_longest_match_info(
        self,
        message: AnyStr,
        commands: Sequence[Optional[Command]],
        command_methods: Sequence[Callable],
    ) -> Optional[MatchInfo]:
        """Find the longest command that matches the start of the message.

        Loops over all registered commands and attempts to match them to the beginning
        of the message. Of those that do match, the match that matches the longest
        portion of the message is chosen. The length of the match, the matched command
        and corresponding method, as well as the captured arguments fro the match are
        returned wrapped as a MatchInfo object.

        Args:
            message (AnyStr): The message being handled by the interpreter.
            commands (List[Command]): The commands registered in the adapter.
            command_methods (List[Callable]): The methods corresponding to the commands.

        Returns:
            Optional[MatchInfo]:
                Information about the command matching the longest portion of the start
                of the handled message wrapped in a MatchInfo object. Returns None if
                no match is found.
        """
        match_length = None
        command_method = None
        command_args = None
        match_command = None
        for command, method in zip(commands, command_methods):
            if command is None:
                continue
            parse_result = command.parse(message)
            if parse_result is None:
                continue
            args, match_start, match_end, _ = parse_result
            if match_start != 0:
                continue
            if match_length is None:
                match_length = match_end
            if match_end >= match_length:
                match_length = match_end
                command_method = method
                command_args = args
                match_command = command
        if (
            match_length is not None
            and match_command is not None
            and command_method is not None
            and command_args is not None
        ):
            return self.MatchInfo(
                match_length, match_command, command_method, command_args
            )
        return None

    async def _execute_command_from_match(self, match_info: MatchInfo):
        """Execute a command specified in a MatchInfo object."""
        args = self._convert_args_to_method_types(
            match_info.command_args, match_info.command_method
        )
        response = await match_info.command_method(*args)
        interrupt = match_info.command.interrupt
        return response, interrupt

    def _get_remaining_message(self, message: AnyStr, match_info: MatchInfo) -> AnyStr:
        """Trim off a matched command from the start of the message and strip."""
        remaining_message = message[match_info.match_length :]
        remaining_message = (
            remaining_message.strip() if self.ignore_whitespace else remaining_message
        )
        return remaining_message

    async def _execute_commands_in_message(
        self, message: AnyStr, command_methods: List[Callable]
    ) -> Optional[Tuple[List[AnyStr], List[bool]]]:
        """Execute commands in a message.

        Given a message and a list of registerd command methods, find commands within
        the message and execute them.

        Args:
            message (AnyStr): The message commands are to be found within.
            command_methods (List[Callable]): A list of registered command methods.

        Returns:
            Optional[tuple[List[AnyStr], List[bool]]]:
                A tuple containing a list of responses to each executed command and a
                list of flags indicating whether each executed command raises an
                interrupt. If no command is found within the message, or the whole
                message cannot be parsed as a series of commands, return None
        """
        commands = [
            cast(Optional[Command], getattr(method, "__command__", None))
            for method in command_methods
        ]
        responses = []
        interrupts = []

        while message:
            longest_match_info = self._get_longest_match_info(
                message, commands, command_methods
            )

            if longest_match_info is None:
                return None

            response, interrupt = await self._execute_command_from_match(
                longest_match_info
            )

            if isinstance(response, AsyncIterable):
                responses.extend([resp async for resp in response])
            else:
                responses.append(response)
            interrupts.append(interrupt)

            message = self._get_remaining_message(message, longest_match_info)
        return responses, interrupts

    async def handle(
        self, adapter: Adapter, message: AnyStr
    ) -> Tuple[AsyncIterable[AnyStr], bool]:
        """Matches the message to adapter commands and calls the corresponding methods.

        An asynchronous method which handles a message by attempting to match the
        message against the registered commands, if matches are found the
        corresponding commands are called and the replies returned with an asynchronous
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
        command_methods: List[Callable] = [
            func for _, func in getmembers(adapter) if hasattr(func, "__command__")
        ]

        message = message.strip() if self.ignore_whitespace else message

        result = await self._execute_commands_in_message(message, command_methods)
        if result is None:
            return self.unknown_command(), False
        responses, interrupts = result

        resp = wrap_messages_as_async_iterable(responses)
        interrupt = any(interrupts)
        return resp, interrupt
