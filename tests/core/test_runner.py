import pytest
from mock import AsyncMock

from tickit.core.runner import run_all_forever


@pytest.mark.asyncio
async def test_run_forever_all_awaits():
    awaitable = AsyncMock()
    await run_all_forever([awaitable()])
    awaitable.assert_awaited_once_with()
