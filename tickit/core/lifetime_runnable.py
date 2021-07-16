import asyncio
import traceback
from typing import Iterable

from tickit.utils.compat.typing_compat import Protocol, runtime_checkable


@runtime_checkable
class LifetimeRunnable(Protocol):
    async def run_forever(self) -> None:
        ...


async def run_all_forever(runnables: Iterable[LifetimeRunnable]) -> None:
    async def run_with_error_handling(runnable: LifetimeRunnable) -> None:
        try:
            await runnable.run_forever()
        except Exception as e:
            print("Task exception: {}".format(e))
            print(traceback.format_exc())

    await asyncio.wait(
        [
            asyncio.create_task(run_with_error_handling(runnable))
            for runnable in runnables
        ]
    )
