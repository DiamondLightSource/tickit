import asyncio
import traceback
from typing import Awaitable, Iterable, List


def run_all(awaitables: Iterable[Awaitable[None]]) -> List[asyncio.Task]:
    """Asynchronously runs the run_forever method of each lifetime runnable.

    Creates and runs an asyncio task for the run_forever method of each lifetime
    runnable. Calls to the run_forever method are wrapped with an error handler.

    Args:
        awaitables: An iterable of awaitable objects.

    Returns:
        List[asyncio.Task]: A list of asyncio tasks for the awaitables.
    """

    async def run_with_error_handling(awaitable: Awaitable[None]) -> None:
        try:
            await awaitable
        except Exception as e:
            # These are prints rather than logging because we just want the
            # result going directly to stdout.
            print("Task exception: {}".format(e))
            print(traceback.format_exc())

    return [
        asyncio.create_task(run_with_error_handling(awaitable))
        for awaitable in awaitables
    ]


async def run_all_forever(awaitables: Iterable[Awaitable[None]]) -> None:
    """Asynchronously runs the run_forever method of each lifetime runnable.

    Creates and runs an asyncio task for the run_forever method of each lifetime
    runnable. Calls to the run_forever method are wrapped with an error handler.
    This function blocks until all run_forever methods have completed.

    Args:
        awaitables: An iterable of awaitable objects.
    """
    await asyncio.wait(run_all(awaitables))
