from typing import Callable

from tickit.utils.compat.typing_compat import Protocol, runtime_checkable


@runtime_checkable
class Adapter(Protocol):
    async def run_forever(self) -> None:
        ...

    def command(self, command: object, interrupt: bool) -> Callable:
        def register(func: Callable) -> Callable:
            ...

        return register
