import asyncio
import traceback
from typing import Iterable, List

from tickit.utils.compat.typing_compat import Protocol, runtime_checkable


@runtime_checkable
class LifetimeRunnable(Protocol):
    """An interface for types which implement an awaitable run_forever method."""

    async def run_forever(self) -> None:
        """An asynchronous method which may run indefinitely."""
        pass


def run_all(runnables: Iterable[LifetimeRunnable]) -> List[asyncio.Task]:
    """Asynchronously runs the run_forever method of each lifetime runnable.

    Creates and runs an asyncio task for the run_forever method of each lifetime
    runnable. Calls to the run_forever method are wrapped with an error handler.

    Args:
        runnables: An iterable of objects which implement run_forever.

    Returns:
        List[asyncio.Task]: A list of asyncio tasks for the runnables.
    """

    async def run_with_error_handling(runnable: LifetimeRunnable) -> None:
        try:
            await runnable.run_forever()
        except Exception as e:
            # These are prints rather than logging because we just want the
            # result going directly to stdout.
            print("Task exception: {}".format(e))
            print(traceback.format_exc())

    return [
        asyncio.create_task(run_with_error_handling(runnable)) for runnable in runnables
    ]


async def run_all_forever(runnables: Iterable[LifetimeRunnable]) -> None:
    """Asynchronously runs the run_forever method of each lifetime runnable.

    Creates and runs an asyncio task for the run_forever method of each lifetime
    runnable. Calls to the run_forever method are wrapped with an error handler.
    This function blocks until all run_forever methods have completed.

    Args:
        runnables: An iterable of objects which implement run_forever.
    """
    await asyncio.wait(run_all(runnables))
