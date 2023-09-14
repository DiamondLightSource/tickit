import asyncio
from typing import Iterable

import pytest
from immutables import Map
from mock import AsyncMock, Mock, patch
from mock.mock import create_autospec

from tickit.core.components.component import Component
from tickit.core.components.system_component import SystemComponent, SystemSimulation
from tickit.core.state_interfaces.state_interface import StateConsumer, StateProducer
from tickit.core.typedefs import (
    Changes,
    ComponentID,
    ComponentPort,
    Input,
    Output,
    PortID,
    SimTime,
    StopComponent,
)
from tickit.utils.topic_naming import output_topic


@pytest.fixture
def mock_state_producer_type() -> Mock:
    mock: Mock = create_autospec(StateProducer, instance=False)
    mock.return_value = create_autospec(StateProducer, instance=True)
    return mock


@pytest.fixture
def mock_state_consumer_type() -> Mock:
    return create_autospec(StateConsumer, instance=False)


@pytest.fixture
def patch_scheduler() -> Iterable[Mock]:
    spec = "tickit.core.components.system_component.NestedScheduler"
    with patch(spec, autospec=True) as mock:

        def on_tick(time, changes):
            pass

        mock.return_value = AsyncMock()
        dummy_output = (Changes(Map({PortID("84"): 84})), 3)
        mock.return_value.error = asyncio.Event()
        mock.return_value.on_tick = AsyncMock(spec=on_tick, return_value=dummy_output)
        mock.return_value.setup
        yield mock


@pytest.fixture
def system_simulation(patch_scheduler) -> Component:
    system_simulation_config = SystemSimulation(
        name=ComponentID("test_system_simulation"),
        inputs={PortID("24"): ComponentPort(ComponentID("25"), PortID("23"))},
        components=[],
        expose={PortID("42"): ComponentPort(ComponentID("43"), PortID("44"))},
    )

    return system_simulation_config()


def test_system_simulation_constructor(system_simulation: SystemSimulation):
    pass


@pytest.fixture
def patch_asyncio() -> Iterable[Mock]:
    with patch(
        "tickit.core.components.system_component.asyncio", autospec=True
    ) as mock:
        yield mock


@pytest.mark.asyncio
async def test_system_simulation_methods(
    system_simulation: SystemComponent,
    mock_state_producer_type: Mock,
    mock_state_consumer_type: Mock,
):
    """Test the 'run_forever' and 'on_tick' methods.

    The 'on_tick' method depends on 'run_forever' being called first. Therefore tests
    for both methods have been bundled together. The test succeeds if the mock state
    interfaces of the system simulation are awaited once with the correct parameters.
    """
    await system_simulation.run_forever(
        mock_state_consumer_type, mock_state_producer_type  # type: ignore
    )

    system_simulation.state_consumer.subscribe.assert_awaited_once()  # type: ignore
    time = SimTime(0)
    (
        expected_changes,
        expected_call_back,
    ) = system_simulation.scheduler.on_tick.return_value  # type: ignore
    await system_simulation.on_tick(time, expected_changes)

    system_simulation.state_producer.produce.assert_awaited_once_with(  # type: ignore
        output_topic(system_simulation.name),
        Output(system_simulation.name, time, expected_changes, expected_call_back),
    )


@pytest.mark.asyncio
async def test_system_simulation_handles_exception_in_handle_input(
    system_simulation: SystemComponent,
    mock_state_producer_type: Mock,
    mock_state_consumer_type: Mock,
):
    await system_simulation.run_forever(
        mock_state_consumer_type, mock_state_producer_type  # type: ignore
    )

    def raise_error(time, changes):
        raise RuntimeError("Test exception")

    system_simulation.on_tick = AsyncMock()  # type: ignore
    system_simulation.on_tick.side_effect = raise_error
    await system_simulation.handle_input(
        Input(ComponentID("Test"), SimTime(42), Changes(Map()))
    )
    system_simulation.on_tick.assert_awaited_once_with(SimTime(42), Changes(Map()))
    system_simulation.state_producer.produce.assert_awaited_once()  # type: ignore


@pytest.mark.asyncio
async def test_system_simulation_stops_when_told(
    system_simulation: SystemComponent,
    mock_state_producer_type: Mock,
    mock_state_consumer_type: Mock,
):
    await system_simulation.run_forever(
        mock_state_consumer_type, mock_state_producer_type  # type: ignore
    )

    await system_simulation.handle_input(StopComponent())
    assert all(map(lambda task: task.done(), system_simulation._tasks))
