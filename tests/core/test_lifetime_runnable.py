from unittest.mock import MagicMock

import pytest

from tickit.core.lifetime_runnable import run_all_forever


class TestLifetimeRunnable:
    async def run_forever(self) -> None:
        while True:
            pass


@pytest.mark.asyncio
async def test_run_all_forever_runs():
    test_lifetime_runnable = TestLifetimeRunnable()
    test_lifetime_runnable.run_forever = MagicMock()  # type: ignore
    await run_all_forever([test_lifetime_runnable.run_forever()])
    test_lifetime_runnable.run_forever.assert_called_once_with()
