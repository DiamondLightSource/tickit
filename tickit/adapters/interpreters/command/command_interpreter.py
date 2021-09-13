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
    interrupt: bool

    @abstractmethod
    def parse(self, data: bytes) -> Optional[Sequence[AnyStr]]:
        pass


class CommandInterpreter:
    @staticmethod
    async def _wrap(resp: AnyStr) -> AsyncIterable[AnyStr]:
        yield resp

    @staticmethod
    async def unknown_command() -> AsyncIterable[bytes]:
        yield b"Request does not match any known command"

    async def handle(
        self, adapter: Adapter, message: bytes
    ) -> Tuple[AsyncIterable[Union[str, bytes]], bool]:

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
