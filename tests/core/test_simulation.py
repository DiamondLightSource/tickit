import asyncio
from typing import AsyncGenerator, DefaultDict, Dict, Iterable

import pytest
import pytest_asyncio
from mock import AsyncMock, Mock, create_autospec, patch

from tickit.core.components.component import Component
from tickit.core.management.event_router import Wiring
from tickit.core.management.schedulers.master import MasterScheduler
from tickit.core.management.ticker import Ticker
from tickit.core.simulation import TickitSimulation, TickitSimulationBuilder
from tickit.core.state_interfaces.state_interface import StateConsumer, StateProducer
from tickit.core.typedefs import ComponentID, SimTime


def test_builder_scheduler_and_components_included_by_default() -> None:
    tickit_simulation_builder = TickitSimulationBuilder("tests/core/sim.yaml")

    assert tickit_simulation_builder._include_components is True
    assert tickit_simulation_builder._include_schedulers is True


def test__builder_backend_internal_by_default() -> None:
    tickit_simulation_builder = TickitSimulationBuilder("tests/core/sim.yaml")

    assert tickit_simulation_builder._backend == "internal"


def test_builder_choose_components_to_run() -> None:
    tickit_simulation_builder = TickitSimulationBuilder(
        "tests/core/sim.yaml",
        components_to_run={ComponentID("source")},
    )
    assert tickit_simulation_builder._components_to_run == {"source"}


def test_builder_default_includes_all_components_in_simulation() -> None:
    tickit_simulation_builder = TickitSimulationBuilder("tests/core/sim.yaml")
    assert tickit_simulation_builder._components_to_run == set()

    tickit_simulation = tickit_simulation_builder.build()
    assert set(tickit_simulation._components.keys()) == {  # type: ignore
        "source",
        "sink",
    }


def test_choosing_all_components_equivalent_to_choosing_none() -> None:
    tickit_simulation_builder = TickitSimulationBuilder(
        "tests/core/sim.yaml",
        components_to_run={ComponentID("source"), ComponentID("sink")},
    )
    tickit_simulation = tickit_simulation_builder.build()

    tickit_simulation_builder_2 = TickitSimulationBuilder("tests/core/sim.yaml")
    tickit_simulation_2 = tickit_simulation_builder_2.build()

    assert (
        tickit_simulation._components.keys()  # type: ignore
        == tickit_simulation_2._components.keys()  # type: ignore
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
        yield asyncio.create_task(asyncio.sleep(2))


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
async def test_running_only_scheduler_does_not_start_component_tasks(
    mock_master_scheduler,
    backend="internal",
) -> None:
    tickit_simulation = TickitSimulation(backend, mock_master_scheduler, None)

    assert isinstance(tickit_simulation._scheduler, MasterScheduler)
    assert tickit_simulation._components is None

    start_scheduler = next(tickit_simulation._start_scheduler_tasks())  # type: ignore
    assert isinstance(start_scheduler, asyncio.Task)

    start_component = next(
        tickit_simulation._start_component_tasks(),  # type: ignore
        None,
    )
    assert start_component is None


@pytest.fixture
def mock_components() -> Dict[ComponentID, Component]:
    return DefaultDict()


@pytest.mark.skip
@pytest.mark.asyncio
async def test_running_only_one_component() -> None:
    pass


@pytest.mark.skip
@pytest.mark.asyncio
async def test_running_scheduler_and_one_component() -> None:
    pass


@pytest.mark.skip
@pytest.mark.asyncio
async def test_running_only_all_components() -> None:
    pass


@pytest.mark.skip
@pytest.mark.asyncio
async def test_running_all() -> None:
    pass


@pytest.fixture
def patch_tickit_simulation_start_scheduler_tasks() -> Iterable[asyncio.Task]:
    with patch(
        "tickit.core.simulation.TickitSimulation._start_scheduler_tasks", autospec=True
    ) as mock:
        yield mock


@pytest.fixture
def patch_tickit_simulation_start_component_tasks() -> Iterable[asyncio.Task]:
    with patch(
        "tickit.core.simulation.TickitSimulation._start_component_tasks", autospec=True
    ) as mock:
        yield mock


@pytest.mark.asyncio
async def test_running_only_scheduler_calls_both_start_tasks(
    mock_master_scheduler,
    patch_tickit_simulation_start_component_tasks,
    patch_tickit_simulation_start_scheduler_tasks,
    backend="internal",
) -> None:
    tickit_simulation = TickitSimulation(backend, mock_master_scheduler, None)

    assert isinstance(tickit_simulation._scheduler, MasterScheduler)
    assert tickit_simulation._components is None

    await tickit_simulation.run()

    patch_tickit_simulation_start_scheduler_tasks.assert_called_once()
    patch_tickit_simulation_start_component_tasks.assert_called_once()
