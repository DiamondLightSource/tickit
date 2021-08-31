from typing import Type
from unittest.mock import MagicMock

import pytest

from tickit.core.lifetime_runnable import LifetimeRunnable, run_all_forever


@pytest.fixture
def TestLifetimeRunnable():
    class TestLifetimeRunnable:
        async def run_forever(self) -> None:
            while True:
                pass

    return TestLifetimeRunnable


@pytest.mark.asyncio
async def test_run_all_forever_runs(TestLifetimeRunnable: Type[LifetimeRunnable]):
    test_lifetime_runnable = TestLifetimeRunnable()
    test_lifetime_runnable.run_forever = MagicMock()  # type: ignore
    await run_all_forever([test_lifetime_runnable])
    test_lifetime_runnable.run_forever.assert_called_once_with()
