from typing import Iterable

import pytest
from mock import AsyncMock, Mock, create_autospec, patch

from tickit.core.management.event_router import Wiring
from tickit.core.management.schedulers.master import MasterScheduler
from tickit.core.management.ticker import Ticker
from tickit.core.state_interfaces.state_interface import StateConsumer, StateProducer


@pytest.fixture
def mock_wiring() -> Mock:
    return create_autospec(Wiring, instance=True)


@pytest.fixture
def mock_state_consumer() -> Mock:
    return create_autospec(StateConsumer, instance=False)


@pytest.fixture
def mock_state_producer() -> Mock:
    return create_autospec(StateProducer, instance=False)


@pytest.fixture
def patch_ticker() -> Iterable[Mock]:
    with patch("tickit.core.management.schedulers.base.Ticker", autospec=True) as mock:
        mock.return_value = AsyncMock(spec_set=Ticker)
        yield mock


@pytest.fixture
@pytest.mark.asyncio
async def master_scheduler(
    mock_wiring, mock_state_consumer, mock_state_producer, patch_ticker
) -> MasterScheduler:
    master_scheduler = MasterScheduler(
        mock_wiring, mock_state_consumer, mock_state_producer
    )
    await master_scheduler.setup()
    return master_scheduler


def test_master_scheduler_constructor_and_setup_methods(
    master_scheduler: MasterScheduler,
):
    pass


@pytest.fixture
def patch_asyncio() -> Iterable[Mock]:
    with patch(
        "tickit.core.management.schedulers.master.asyncio", autospec=True
    ) as mock:
        yield mock


@pytest.mark.asyncio
async def test_master_scheduler_run_tick_methods(
    master_scheduler: MasterScheduler, patch_asyncio
):
    await master_scheduler._run_initial_tick()
    await master_scheduler._run_tick()
