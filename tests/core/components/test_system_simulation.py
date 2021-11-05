import asyncio
from typing import Any, Awaitable, Callable, Iterable

import pytest
from immutables import Map
from mock import AsyncMock, Mock, patch
from mock.mock import create_autospec

from tickit.core.components.component import Component
from tickit.core.components.system_simulation import (
    SystemSimulation,
    SystemSimulationComponent,
)
from tickit.core.state_interfaces.state_interface import StateConsumer, StateProducer
from tickit.core.typedefs import (
    Changes,
    ComponentID,
    ComponentPort,
    Output,
    PortID,
    SimTime,
)
from tickit.utils.topic_naming import output_topic


class MockStateConsumer:
    @staticmethod
    def __call__(callback: Callable[[Any], Awaitable[None]]) -> None:
        return create_autospec(StateConsumer)


class MockStateProducer:
    @staticmethod
    def __call__():
        return create_autospec(StateProducer)


@pytest.fixture
def patch_scheduler() -> Iterable[Mock]:
    spec = "tickit.core.components.system_simulation.SlaveScheduler"
    with patch(spec, autospec=True) as mock:

        def on_tick(time, changes):
            pass

        mock.return_value = AsyncMock()
        dummy_output = (Changes(Map({PortID("84"): 84})), 3)
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
        "tickit.core.components.system_simulation.asyncio", autospec=True
    ) as mock:
        yield mock


@pytest.fixture
def patch_run_all() -> Iterable[Mock]:
    with patch(
        "tickit.core.components.system_simulation.run_all", autospec=True
    ) as mock:
        mock.return_value = [asyncio.sleep(0)]
        yield mock


@pytest.mark.asyncio
async def test_system_simulation_methods(
    system_simulation: SystemSimulationComponent,
    patch_run_all: Mock,
):
    """Test the 'run_forever' and 'on_tick' methods.

    The 'on_tick' method depends on 'run_forever' being called first. Therefore tests
    for both methods have been bundled together. The test succeeds if the mock state
    interfaces of the system simulation are awaited once with the correct parameters.
    """
    await system_simulation.run_forever(
        MockStateConsumer(), MockStateProducer()  # type: ignore
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
