from inspect import getmembers
from typing import (
    AnyStr,
    AsyncIterable,
    Callable,
    List,
    Optional,
    Tuple,
    cast,
    get_type_hints,
)

from tickit.adapters.interpreters.command.command_interpreter import Command
from tickit.core.adapter import Adapter, Interpreter


class MultiCommandInterpreter(Interpreter[AnyStr, AnyStr]):
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

    async def _wrap_messages_as_async_iterable(self, messages: List[AnyStr]):
        for message in messages:
            yield message

    @staticmethod
    def _convert_args_to_method_types(arg_strings, method):
        args = (
            argtype(arg)
            for arg, argtype in zip(arg_strings, get_type_hints(method).values())
        )
        return args

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

        commands = [
            cast(Optional[Command[AnyStr]], getattr(method, "__command__", None))
            for method in command_methods
        ]

        remaining_message = message
        if self.ignore_whitespace:
            remaining_message = remaining_message.strip()
        responses = []
        interrupts = []
        while remaining_message:

            longest_match_length = 0
            matched_command = None
            matched_command_method = None
            matched_command_args = None

            for command, method in zip(commands, command_methods):
                if command is None:
                    continue
                parse_result = command.parse(remaining_message)
                if parse_result is None:
                    continue
                args, match_start, match_end = parse_result
                if args is None:
                    continue
                if match_start != 0:
                    continue
                if match_end > longest_match_length:
                    longest_match_length = match_end
                    matched_command_method = method
                    matched_command_args = args
                    matched_command = command

            if matched_command_method is None or matched_command is None:
                resp = MultiCommandInterpreter.unknown_command()
                return (
                    resp,
                    False,
                )

            args = self._convert_args_to_method_types(
                matched_command_args, matched_command_method
            )

            response = await matched_command_method(*args)
            interrupt = matched_command.interrupt
            responses.append(response)
            interrupts.append(interrupt)
            remaining_message = remaining_message[longest_match_length:]
            if self.ignore_whitespace:
                remaining_message = remaining_message.strip()

        resp = self._wrap_messages_as_async_iterable(responses)
        interrupt = any(interrupts)
        return resp, interrupt
