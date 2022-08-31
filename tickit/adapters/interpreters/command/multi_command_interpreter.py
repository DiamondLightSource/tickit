import re
from inspect import getmembers
from typing import AnyStr, AsyncIterable, Callable, Dict, List, Tuple, get_type_hints

from tickit.adapters.interpreters.utils import wrap_as_async_iterable
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
    def _get_longest_regex_match(regexes: List[str], message: str):
        longest_match = None
        for regex in regexes:
            match = re.match(regex, message)
            if match is not None:
                if longest_match is None:
                    longest_match = match
                    continue
                elif match.end() > longest_match.end():
                    longest_match = match
        return longest_match

    @staticmethod
    def _get_args_from_command_regex_match(longest_match: re.Match):
        command_method_name = longest_match.lastgroup
        if command_method_name is not None:
            arg_strings = [
                value
                for value in longest_match.groups()
                if value is not None
                and value != longest_match.groupdict()[command_method_name]
            ]
            return arg_strings

    async def _wrap_messages_as_async_iterable(self, messages: list[AnyStr]):
        for message in messages:
            yield message

    @staticmethod
    def _convert_args_to_method_types(arg_strings, method):
        args = (
            argtype(arg)
            for arg, argtype in zip(arg_strings, get_type_hints(method).values())
        )
        return args

    def _remove_match_from_message(self, message, regex_match):
        group_to_remove = regex_match.lastgroup
        cut_index = regex_match.end(group_to_remove)
        remaining_message = message[cut_index:]
        if self.ignore_whitespace:
            remaining_message = remaining_message.strip()
        return remaining_message

    async def _execute_matching_command(self, regex_match, command_method):
        arg_strings = self._get_args_from_command_regex_match(regex_match)
        args = self._convert_args_to_method_types(arg_strings, command_method)
        response = await command_method(*args)
        return response

    async def _parse_and_execute_commands_from_message(
        self, command_methods: dict, regexes: List[str], message: str
    ):
        remaining_message = message
        responses = []
        interrupts = []
        while remaining_message:
            longest_match = self._get_longest_regex_match(regexes, remaining_message)
            if longest_match is None:
                return (
                    wrap_as_async_iterable(b"Command unknown"),
                    False,
                )
            else:
                command_method = command_methods[longest_match.lastgroup]
                response = await self._execute_matching_command(
                    longest_match, command_method
                )
                interrupt = command_method.__command__.interrupt
                responses.append(response)
                interrupts.append(interrupt)
                remaining_message = self._remove_match_from_message(
                    remaining_message, longest_match
                )
        resp = self._wrap_messages_as_async_iterable(responses)
        interrupt = any(interrupts)
        return resp, interrupt

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
        if isinstance(message, bytes):
            decoded_message = message.decode()
        else:
            decoded_message = message

        command_methods: Dict[str, Callable] = {
            name: func
            for name, func in getmembers(adapter)
            if hasattr(func, "__command__")
        }
        commands = [
            getattr(command_methods[func], "__command__", None)
            for func in command_methods
        ]
        regexes = [
            f"(?P<{func}>{command.regex.decode()})"
            for command, func in zip(commands, command_methods)
            if command is not None
        ]
        resp, interrupt = await self._parse_and_execute_commands_from_message(
            command_methods, regexes, decoded_message
        )
        return resp, interrupt
