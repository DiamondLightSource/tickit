from typing import Callable

from tickit.utils.compat.typing import Protocol, runtime_checkable


@runtime_checkable
class Adapter(Protocol):
    async def run_forever(self) -> None:
        ...

    def command(self, *args, interrupt: bool = False) -> Callable:
        def register(func: Callable) -> Callable:
            ...

        return register
