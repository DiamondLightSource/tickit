import asyncio
from typing import AsyncGenerator, Dict, Iterable

import pytest
import pytest_asyncio
from mock import AsyncMock, Mock, create_autospec, patch

from tickit.core.components.component import Component
from tickit.core.management.event_router import Wiring
from tickit.core.management.schedulers.master import MasterScheduler
from tickit.core.management.ticker import Ticker
from tickit.core.simulation import TickitSimulation, build_simulation
from tickit.core.state_interfaces.state_interface import StateConsumer, StateProducer
from tickit.core.typedefs import ComponentID, SimTime
from tickit.devices.sink import Sink
from tickit.devices.source import Source


def test_builder_scheduler_and_components_included_by_default() -> None:
    tickit_simulation = build_simulation("tests/core/sim.yaml")

    assert tickit_simulation._scheduler is not None
    assert tickit_simulation._components is not None


def test__builder_backend_internal_by_default() -> None:
    tickit_simulation = build_simulation("tests/core/sim.yaml")

    assert tickit_simulation._backend == "internal"


def test_builder_choose_components_to_run() -> None:
    tickit_simulation = build_simulation(
        "tests/core/sim.yaml",
        components_to_run={ComponentID("source")},
    )

    assert tickit_simulation._components is not None
    assert tickit_simulation._components.keys() == {"source"}
    assert len(tickit_simulation._components) == 1


def test_builder_default_includes_all_components_in_simulation() -> None:
    tickit_simulation = build_simulation("tests/core/sim.yaml")

    assert tickit_simulation._components is not None
    assert tickit_simulation._components.keys() == {
        "source",
        "sink",
    }


def test_choosing_all_components_equivalent_to_choosing_none() -> None:
    tickit_simulation = build_simulation(
        "tests/core/sim.yaml",
        components_to_run={ComponentID("source"), ComponentID("sink")},
    )
    tickit_simulation_2 = build_simulation("tests/core/sim.yaml")

    assert tickit_simulation._components is not None
    assert tickit_simulation_2._components is not None
    assert (
        tickit_simulation._components.keys() == tickit_simulation_2._components.keys()
    )


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
async def patch_run_forever() -> AsyncGenerator:
    with patch(
        "tickit.core.management.schedulers.master.MasterScheduler.run_forever",
        autospec=True,
    ):
        yield asyncio.create_task(asyncio.sleep(1))


@pytest_asyncio.fixture
async def mock_master_scheduler(
    mock_wiring,
    mock_state_consumer,
    mock_state_producer,
    patch_ticker,
    patch_run_forever,
) -> MasterScheduler:
    mock_master_scheduler = MasterScheduler(
        mock_wiring, mock_state_consumer, mock_state_producer
    )
    await mock_master_scheduler.setup()
    return mock_master_scheduler


@pytest.mark.asyncio
async def test_running_only_scheduler(
    mock_master_scheduler: MasterScheduler,
) -> None:
    tickit_simulation = TickitSimulation(
        backend="internal", scheduler=mock_master_scheduler, components=None
    )
    assert tickit_simulation._components is None
    assert tickit_simulation._scheduler is not None

    await tickit_simulation.run()

    tickit_simulation._scheduler.run_forever.assert_called_once()  # type: ignore


@pytest_asyncio.fixture
async def patch_component_run_forever() -> AsyncGenerator:
    with patch(
        "tickit.core.components.device_component.DeviceComponent.run_forever",
        autospec=True,
    ) as mock:
        mock.return_value = asyncio.create_task(asyncio.sleep(1))
        yield mock


@pytest.fixture
def mock_components() -> Dict[ComponentID, Component]:
    sink = Sink(name=ComponentID("test_sink"), inputs=dict())
    source = Source(name=ComponentID("test_source"), inputs=dict(), value=42)
    mock_components = {
        ComponentID("test_sink"): sink(),
        ComponentID("test_source"): source(),
    }
    return mock_components


@pytest.mark.asyncio
async def test_running_only_components(
    patch_component_run_forever: Mock,
    mock_components: Dict[ComponentID, Component],
) -> None:
    tickit_simulation = TickitSimulation(
        backend="internal", scheduler=None, components=mock_components
    )
    assert tickit_simulation._scheduler is None
    assert tickit_simulation._components is not None

    await tickit_simulation.run()

    assert patch_component_run_forever.call_count == len(tickit_simulation._components)


@pytest.mark.asyncio
async def test_running_all(
    mock_master_scheduler: MasterScheduler,
    patch_component_run_forever: Mock,
    mock_components: Dict[ComponentID, Component],
) -> None:
    tickit_simulation = TickitSimulation(
        backend="internal", scheduler=mock_master_scheduler, components=mock_components
    )
    assert tickit_simulation._scheduler is not None
    assert tickit_simulation._components is not None

    await tickit_simulation.run()

    tickit_simulation._scheduler.run_forever.assert_called_once()  # type: ignore
    assert patch_component_run_forever.call_count == len(tickit_simulation._components)
