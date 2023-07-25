import asyncio

import pytest


@pytest.fixture
def event_loop():
    """Manage instance of event loop for runner test cases."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()
