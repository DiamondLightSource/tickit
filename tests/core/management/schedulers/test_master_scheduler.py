import asyncio
from typing import Awaitable, Iterable, Set

import pytest
import pytest_asyncio
from mock import AsyncMock, Mock, create_autospec, patch

from tickit.core.management.event_router import Wiring
from tickit.core.management.schedulers.master import MasterScheduler
from tickit.core.management.ticker import Ticker
from tickit.core.state_interfaces.state_interface import StateConsumer, StateProducer
from tickit.core.typedefs import ComponentException, ComponentID, SimTime


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
        mock.return_value = AsyncMock(spec=Ticker)
        mock.return_value.components = ["test"]
        mock.return_value.time = SimTime(41)
        mock.return_value.finished = asyncio.Event()
        yield mock


@pytest_asyncio.fixture
async def master_scheduler(
    mock_wiring,
    mock_state_consumer,
    mock_state_producer,
    patch_ticker,
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
def patch_asyncio_wait() -> Iterable[Mock]:
    """A patch over the method asyncio.wait.

    This fixture patches over asyncio.wait to prevent the test from waiting
    indefinitely.The method is replaced with a new callable that simulates the
    outcome of the asyncio.wait method in order to cover most of the tested function.
    """

    class wait:
        def __init__(self):
            self.call_count = 0
            self.threshold = 3

        async def __call__(self, awaitables: Set[Awaitable], return_when):
            """Simulates the call to asyncio.wait(return_when=FIRST_COMPLETED).

            The call to wait is a (deliberate) race condition. To simulate this and
            test all parts of the code, this method switches its response depending
            on how many times it's been called.
            """
            for aw in awaitables:
                await aw

            if self.call_count < self.threshold:
                self.call_count += 1
                return [list(awaitables)[0]], None
            else:
                self.call_count += 1
                return [list(awaitables)[1]], None

    with patch(
        "tickit.core.management.schedulers.master.asyncio.wait",
        new_callable=wait,
    ) as mock:
        yield mock


@pytest.fixture
def patch_asyncio_Event() -> Iterable[Mock]:
    """A patch over the asyncio.Event class. Prevents warnings from being raised."""
    with patch(
        "tickit.core.management.schedulers.master.asyncio.Event", autospec=True
    ) as mock:
        yield mock


@pytest.fixture
def patch_asyncio_sleep() -> Iterable[Mock]:
    with patch(
        "tickit.core.management.schedulers.master.asyncio.sleep", autospec=True
    ) as mock:
        yield mock


@pytest.fixture
def patch_time_ns() -> Iterable[Mock]:
    class frozen_clock:
        def __init__(self):
            self.time = 1000

        def __call__(self):
            return self.time

    with patch(
        "tickit.core.management.schedulers.master.time_ns", new_callable=frozen_clock
    ) as mock:
        yield mock


@pytest.mark.asyncio
async def test_master_scheduler_do_initial_tick(
    master_scheduler: MasterScheduler, patch_time_ns
):
    await master_scheduler.setup()
    await master_scheduler._do_initial_tick()
    assert master_scheduler.last_time == patch_time_ns()


@pytest.mark.asyncio
async def test_master_scheduler_do_tick_method(
    master_scheduler: MasterScheduler,
    patch_asyncio_wait,
    patch_asyncio_Event,
    patch_asyncio_sleep,
):
    master_scheduler.add_wakeup(ComponentID("foo"), SimTime(42))
    master_scheduler.add_wakeup(ComponentID("bar"), SimTime(52))
    master_scheduler.add_wakeup(ComponentID("baz"), SimTime(62))
    master_scheduler.add_wakeup(ComponentID("boo"), SimTime(72))
    await master_scheduler.setup()
    await master_scheduler._do_initial_tick()
    await master_scheduler._do_tick()
    assert master_scheduler.wakeups == {"bar": 52, "baz": 62, "boo": 72}
    await master_scheduler._do_tick()
    assert master_scheduler.wakeups == {"baz": 62, "boo": 72}
    await master_scheduler._do_tick()
    assert master_scheduler.wakeups == {"boo": 72}
    # After two ticks `patch_asyncio_wait` will switch to returning:
    # `self.new_wakeup.wait()` instead of `self.sleep_time(when)` (See:
    # tickit/core/management/schedulers/master.py:89). After that we expect wakeups
    # to stop being removed.
    await master_scheduler._do_tick()
    assert master_scheduler.wakeups == {"boo": 72}


@pytest.mark.asyncio
async def test_master_scheduler_schedule_interrupt_method(
    master_scheduler: MasterScheduler, patch_time_ns
):
    await master_scheduler.setup()
    await master_scheduler._do_initial_tick()
    assert master_scheduler.wakeups == {}
    await master_scheduler.schedule_interrupt(ComponentID("foo"))
    assert master_scheduler.wakeups == {"foo": master_scheduler.ticker.time}


@pytest.mark.asyncio
async def test_schedule_interrupt_succeeds_with_queued_wakeup(
    master_scheduler: MasterScheduler, patch_time_ns
):
    master_scheduler.add_wakeup(ComponentID("bar"), SimTime(42))
    await master_scheduler.setup()
    await master_scheduler._do_initial_tick()
    assert master_scheduler.wakeups == {"bar": 42}
    await master_scheduler.schedule_interrupt(ComponentID("me first"))
    assert master_scheduler.wakeups == {
        "me first": master_scheduler.ticker.time,
        "bar": 42,
    }


@pytest.mark.asyncio
async def test_master_scheduler_handle_exception_message(
    master_scheduler: MasterScheduler,
):
    message = ComponentException(
        ComponentID("Test"), Exception("Test exception"), "test exception traceback"
    )
    await master_scheduler.handle_message(message)
    assert master_scheduler.error.is_set()
