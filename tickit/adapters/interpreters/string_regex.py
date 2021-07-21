import re
from dataclasses import dataclass
from typing import Any, Callable, List, Optional, Sequence, Tuple

from tickit.core.adapter import Adapter


@dataclass
class RegexCommand:
    regex: str
    func: Callable[..., str]
    interrupt: bool

    def parse(self, message: str) -> Optional[Sequence[str]]:
        match = re.fullmatch(self.regex, message)
        if match:
            # TODO: Check if matched args are of correct type
            return match.groups()
        return None

    def __call__(self, adapter: Adapter, *args: Sequence[Any]) -> Tuple[str, bool]:
        return self.func(adapter, *args), self.interrupt


class StringRegexInterpreter:
    commands: List[RegexCommand]

    def __init__(self) -> None:
        self.commands = list()

    def command(self, regex: str, interrupt: bool = False) -> Callable:
        def register(func: Callable[..., str]) -> Callable:
            self.commands.append(RegexCommand(regex, func, interrupt))
            return func

        return register

    async def handle(self, adapter: Adapter, message: str) -> Tuple[str, bool]:
        for command in self.commands:
            args = command.parse(message)
            if args is not None:
                return command(adapter, *args)
        return "Request does not match any known command", False
