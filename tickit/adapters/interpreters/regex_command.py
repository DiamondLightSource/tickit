import re
from dataclasses import dataclass
from typing import (
    Any,
    AnyStr,
    Callable,
    Generic,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
)

from tickit.core.adapter import Adapter


@dataclass
class RegexCommand(Generic[AnyStr]):
    regex: AnyStr
    func: Callable[..., str]
    interrupt: bool
    format: Optional[str] = None

    def parse(self, data: bytes) -> Optional[Sequence[AnyStr]]:
        message = data.decode(self.format, "ignore").strip() if self.format else data
        if isinstance(message, type(self.regex)):
            match = re.fullmatch(self.regex, message)
            if match:
                # TODO: Check if matched args are of correct type
                return match.groups()
        return None

    def __call__(self, adapter: Adapter, *args: Sequence[Any]) -> Tuple[str, bool]:
        return self.func(adapter, *args), self.interrupt


class RegexInterpreter:
    commands: List[RegexCommand]

    def __init__(self) -> None:
        self.commands = list()

    def command(
        self,
        regex: Union[bytes, str],
        interrupt: bool = False,
        format: Optional[str] = None,
    ) -> Callable:
        def register(func: Callable[..., str]) -> Callable:
            self.commands.append(RegexCommand(regex, func, interrupt, format))
            return func

        return register

    async def handle(self, adapter: Adapter, message: bytes) -> Tuple[str, bool]:
        for command in self.commands:
            args = command.parse(message)
            if args is not None:
                return command(adapter, *args)
        return "Request does not match any known command", False
