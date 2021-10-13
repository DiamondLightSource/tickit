from typing import Any, Iterable

import pytest
from immutables import Map
from mock import AsyncMock, Mock, patch

from tickit.core.components.system_simulation import SystemSimulation
from tickit.core.state_interfaces.internal import (
    InternalStateConsumer,
    InternalStateProducer,
)
from tickit.core.typedefs import Changes, ComponentID, ComponentPort, PortID, SimTime


@pytest.fixture
def mock_scheduler() -> Iterable[Mock]:
    spec = "tickit.core.components.system_simulation.SlaveScheduler"
    with patch(spec, autospec=True) as mock:

        def on_tick(time, changes):
            pass

        mock.return_value = AsyncMock()
        dummy_output = Changes(Map({PortID("42"): 42}))
        mock.return_value.on_tick = AsyncMock(spec=on_tick, side_effect=dummy_output)
        mock.return_value.setup
        yield mock


@pytest.fixture
def system_simulation(mock_scheduler) -> SystemSimulation:
    return SystemSimulation(
        name=ComponentID("test_system_simulation"),
        components=[],
        state_consumer=InternalStateConsumer,
        state_producer=InternalStateProducer,
        expose={PortID("42"): ComponentPort(ComponentID("43"), PortID("44"))},
    )


def test_system_simulation_constructor(system_simulation: SystemSimulation):
    pass


@pytest.fixture
def patch_asyncio() -> Iterable[Mock]:
    with patch(
        "tickit.core.components.system_simulation.asyncio", autospec=True
    ) as mock:
        yield mock


@pytest.mark.asyncio
async def test_system_simulation_run_forever(
    system_simulation: SystemSimulation, patch_asyncio
):
    assert not hasattr(system_simulation, "state_producer")
    assert not hasattr(system_simulation, "state_consumer")

    await system_simulation.run_forever()

    assert hasattr(system_simulation, "state_producer")
    assert hasattr(system_simulation, "state_consumer")

    mock_asyncio: Mock = patch_asyncio
    mock_asyncio.wait.assert_awaited_once()


@pytest.mark.asyncio
async def test_system_simulation_on_tick(system_simulation: SystemSimulation):
    time = SimTime(0)
    changes = Changes(Map({PortID("42"): 42}))

    await system_simulation.set_up_state_interfaces()
    await system_simulation.on_tick(time, changes)

    mock_scheduler: Any = system_simulation.scheduler
    mock_scheduler.on_tick.assert_called_with(time, changes)
