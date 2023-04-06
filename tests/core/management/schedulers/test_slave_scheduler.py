import asyncio
from typing import Dict, Iterable

import pytest
from immutables import Map
from mock import AsyncMock, Mock, create_autospec, patch

from tickit.core.management.event_router import InverseWiring, Wiring
from tickit.core.management.schedulers.slave import SlaveScheduler
from tickit.core.management.ticker import Ticker
from tickit.core.state_interfaces.state_interface import StateConsumer, StateProducer
from tickit.core.typedefs import (
    Changes,
    ComponentException,
    ComponentID,
    ComponentPort,
    Input,
    Output,
    PortID,
    SimTime,
)
from tickit.utils.topic_naming import input_topic


@pytest.fixture
def mock_wiring() -> Mock:
    mock = create_autospec(InverseWiring, instance=True)
    mock[ComponentID("expose")] = create_autospec({})
    return mock


@pytest.fixture
def mock_state_consumer() -> Mock:
    return create_autospec(StateConsumer, instance=False)


@pytest.fixture
def mock_state_producer() -> Mock:
    return create_autospec(StateProducer, instance=False)


@pytest.fixture
def mock_raise_interrupt() -> Mock:
    async def interrupt():
        pass

    return create_autospec(interrupt)


@pytest.fixture
def patch_ticker() -> Iterable[Mock]:
    with patch("tickit.core.management.schedulers.base.Ticker", autospec=True) as mock:
        mock.return_value = AsyncMock(spec=Ticker)
        mock.return_value.components = ["test"]
        mock.return_value.time = SimTime(41)
        mock.return_value.finished = asyncio.Event()
        yield mock


@pytest.fixture
def expose() -> Dict[PortID, ComponentPort]:
    return {PortID("42"): ComponentPort(ComponentID("test_component"), PortID("53"))}


@pytest.fixture
def slave_scheduler(
    mock_wiring,
    mock_state_consumer,
    mock_state_producer,
    expose,
    mock_raise_interrupt,
    patch_ticker,
) -> SlaveScheduler:
    return SlaveScheduler(
        mock_wiring,
        mock_state_consumer,
        mock_state_producer,
        expose,
        mock_raise_interrupt,
    )


def test_construct_slave_scheduler(slave_scheduler, expose):
    pass


@pytest.mark.parametrize(
    "wiring",
    [
        pytest.param(Wiring(), id="Wiring"),
        pytest.param(InverseWiring(), id="InverseWiring"),
    ],
)
def test_slave_scheduler_add_exposing_wiring_static_method(wiring):
    """Method to test the static 'add_exposing_wiring' method of 'SlaveScheduler'.

    This test passes if:
    1) The object returned by the method is an instance of 'InverseWiring' regardless
        of the type of the given 'wiring' object;
    2) The entry for 'ComponentID("expose")' in the 'InverseWiring' object is updated
        with the ports to expose.
    """
    expose = {PortID("42"): ComponentPort(ComponentID("test_component"), PortID("53"))}
    result = SlaveScheduler.add_exposing_wiring(wiring, expose)

    assert isinstance(result, InverseWiring)
    assert result[ComponentID("expose")] == expose


@pytest.fixture
def mock_ticker() -> Mock:
    return AsyncMock(spec_set=Ticker)


@pytest.mark.asyncio
async def test_slave_scheduler_update_external_component(
    slave_scheduler: SlaveScheduler,
    mock_ticker: Ticker,
):
    target = ComponentID("external")
    input = Input(
        target=target,
        time=SimTime(9),
        changes=Changes(Map({PortID("31"): 30})),
    )

    slave_scheduler.ticker = mock_ticker
    slave_scheduler.input_changes = input.changes
    await slave_scheduler.update_component(input)
    mock_ticker.propagate.assert_awaited_once_with(  # type: ignore
        Output(target, input.time, input.changes, None)
    )


@pytest.mark.asyncio
async def test_slave_scheduler_update_exposed_component(
    slave_scheduler: SlaveScheduler,
    mock_ticker: Ticker,
):
    target = ComponentID("expose")
    input = Input(
        target=target,
        time=SimTime(9),
        changes=Changes(Map({PortID("31"): 30})),
    )

    slave_scheduler.ticker = mock_ticker
    await slave_scheduler.update_component(input)
    mock_ticker.propagate.assert_awaited_once_with(  # type: ignore
        Output(target, input.time, Changes(Map()), None)
    )


@pytest.mark.asyncio
async def test_slave_scheduler_update_other_component(
    slave_scheduler: SlaveScheduler,
    mock_ticker: Ticker,
    mock_state_producer: AsyncMock,
):
    target = ComponentID("other")
    input = Input(
        target=target,
        time=SimTime(9),
        changes=Changes(Map({PortID("31"): 30})),
    )

    slave_scheduler.ticker = mock_ticker
    slave_scheduler.state_producer = mock_state_producer
    await slave_scheduler.update_component(input)
    mock_state_producer.produce.assert_awaited_once_with(input_topic(target), input)


@pytest.mark.asyncio
async def test_slave_scheduler_run_forever_method(slave_scheduler: SlaveScheduler):
    await slave_scheduler.run_forever()


@pytest.mark.asyncio
async def test_slave_scheduler_on_tick_method(
    slave_scheduler: SlaveScheduler, mock_ticker: Mock
):
    changes = Changes(Map({PortID("67"): 67}))
    slave_scheduler.ticker = mock_ticker
    output_changes, call_at = await slave_scheduler.on_tick(SimTime(8), changes)
    assert output_changes == Changes(Map())
    assert call_at is None


@pytest.mark.asyncio
async def test_slave_scheduler_on_tick_method_with_wakeups(
    slave_scheduler: SlaveScheduler, mock_ticker: Mock
):
    changes = Changes(Map({PortID("67"): 67}))
    slave_scheduler.ticker = mock_ticker
    slave_scheduler.wakeups = {
        ComponentID("first"): SimTime(1),
        ComponentID("second"): SimTime(2),
    }
    output_changes, call_at = await slave_scheduler.on_tick(SimTime(1), changes)
    assert output_changes == Changes(Map())
    assert call_at == SimTime(2)


@pytest.mark.asyncio
async def test_slave_scheduler_schedule_interrupt_method(
    slave_scheduler: SlaveScheduler,
):
    interrupt = ComponentID("interrupt")
    await slave_scheduler.schedule_interrupt(interrupt)
    assert interrupt in slave_scheduler.interrupts


@pytest.mark.asyncio
async def test_slave_scheduler_handle_exception_message(
    slave_scheduler: SlaveScheduler,
):
    await slave_scheduler.setup()
    message = ComponentException(
        ComponentID("Test"), Exception("Test exception"), "test exception traceback"
    )
    await slave_scheduler.handle_message(message)
    assert slave_scheduler.error.is_set()
    assert slave_scheduler.component_error == message
