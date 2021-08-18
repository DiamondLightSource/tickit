import re
from dataclasses import dataclass
from typing import (
    Any,
    AnyStr,
    AsyncIterable,
    Awaitable,
    Callable,
    Generic,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
)

from tickit.core.adapter import Adapter

CommandFunc = Union[
    Callable[..., Awaitable[AnyStr]], Callable[..., AsyncIterable[AnyStr]]
]


@dataclass(frozen=True)
class RegexCommand(Generic[AnyStr]):
    regex: AnyStr
    func: CommandFunc
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

    @staticmethod
    async def _wrap(resp: AnyStr) -> AsyncIterable[AnyStr]:
        yield resp

    async def __call__(
        self, adapter: Adapter, *args: Any
    ) -> Tuple[AsyncIterable[AnyStr], bool]:

        resp = self.func(adapter, *args)
        if not isinstance(resp, AsyncIterable):
            resp = RegexCommand._wrap(await resp)
        return resp, self.interrupt


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
        def register(func: CommandFunc) -> Callable:
            self.commands.append(RegexCommand(regex, func, interrupt, format))
            return func

        return register

    @staticmethod
    async def unknown_command() -> AsyncIterable[bytes]:
        yield b"Request does not match any known command"

    async def handle(
        self, adapter: Adapter, message: bytes
    ) -> Tuple[AsyncIterable[Union[str, bytes]], bool]:
        for command in self.commands:
            args = command.parse(message)
            if args is not None:
                return await command(adapter, *args)
        return RegexInterpreter.unknown_command(), False
