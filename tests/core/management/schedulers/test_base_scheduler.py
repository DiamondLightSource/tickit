from typing import Any, Iterable, Type, Union

import pytest
from immutables import Map
from mock import Mock, create_autospec, patch

from tickit.core.management.event_router import InverseWiring, Wiring
from tickit.core.management.schedulers.base import BaseScheduler
from tickit.core.state_interfaces.state_interface import StateConsumer, StateProducer
from tickit.core.typedefs import (
    Changes,
    ComponentID,
    Input,
    Interrupt,
    Output,
    PortID,
    SimTime,
)


class _TestBaseScheduler(BaseScheduler):
    def __init__(
        self,
        wiring: Union[Wiring, InverseWiring],
        state_consumer: Type[StateConsumer],
        state_producer: Type[StateProducer],
    ):
        super().__init__(wiring, state_consumer, state_producer)
        self.schedule_interrupt_called = False
        self.schedule_interrupt_call_count = 0

    async def schedule_interrupt(self, source: ComponentID) -> None:
        self.schedule_interrupt_called = True
        self.schedule_interrupt_call_count += 1
        return None


@pytest.fixture
def mock_wiring() -> Mock:
    return create_autospec(Wiring, instance=True)


@pytest.fixture
def mock_state_consumer_type() -> Mock:
    return create_autospec(StateConsumer, instance=False)


@pytest.fixture
def mock_state_producer_type() -> Mock:
    return create_autospec(StateProducer, instance=False)


@pytest.fixture
def patch_ticker() -> Iterable[Mock]:
    with patch("tickit.core.management.schedulers.base.Ticker", autospec=True) as mock:
        yield mock


@pytest.fixture
@pytest.mark.asyncio
async def base_scheduler(
    mock_wiring: Mock, mock_state_consumer_type, mock_state_producer_type, patch_ticker
) -> _TestBaseScheduler:
    base_scheduler = _TestBaseScheduler(
        mock_wiring, mock_state_consumer_type, mock_state_producer_type
    )
    await base_scheduler.setup()
    return base_scheduler


def test_base_scheduler_constructor_and_setup(base_scheduler):
    pass


@pytest.mark.asyncio
async def test_base_scheduler_update_component_method(
    base_scheduler: Any,
):
    _input = Input(
        ComponentID("foo"), SimTime(0), Changes(Map({PortID("42"): "hello"}))
    )
    await base_scheduler.update_component(_input)
    base_scheduler.state_producer.produce.assert_awaited_once()


@pytest.mark.asyncio
async def test_base_scheduler_handle_output_message(base_scheduler: Any):
    message = Output(
        ComponentID("bar"),
        SimTime(42),
        Changes(Map({PortID("42"): "world"})),
        SimTime(88),
    )
    await base_scheduler.handle_message(message)
    base_scheduler.ticker.propagate.assert_awaited_once_with(message)


@pytest.mark.asyncio
async def test_base_scheduler_handle_interrupt_message(
    base_scheduler: _TestBaseScheduler,
):
    message = Interrupt(ComponentID("foo"))
    await base_scheduler.handle_message(message)
    assert base_scheduler.schedule_interrupt_call_count == 1


def test_base_scheduler_get_first_wakeups_method(base_scheduler: _TestBaseScheduler):
    expected_component = ComponentID("foo")
    expected_when = SimTime(42)
    base_scheduler.add_wakeup(expected_component, expected_when)

    components, when = base_scheduler.get_first_wakeups()

    assert components == {expected_component}
    assert when == expected_when


def test_base_scheduler_get_empty_wakeups(base_scheduler: _TestBaseScheduler):
    components, when = base_scheduler.get_first_wakeups()
    assert components == set()
    assert when is None
