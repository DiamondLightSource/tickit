from typing import Iterable, List, Optional, Set

import pytest
import pytest_asyncio
from mock import Mock, patch

from tickit.core.simulation import TickitSimulation
from tickit.core.typedefs import ComponentID


# make a fixture which is a TickitSimulation with parts mocked out?
@pytest.fixture
def mock_tickit_simulation(
    fake_config_path: str,
    backend: str,
    include_schedulers: bool,
    include_components: bool,
    components_to_run: Optional[Set[ComponentID]],
) -> TickitSimulation:
    tickit_simulation = TickitSimulation(
        fake_config_path,
        backend,
        include_schedulers,
        include_components,
    )


# use a real TickitSimulation, just mock out the creating of the tasks
# so no tasks are created?
@pytest.fixture
def patch_asyncio_create_task() -> Iterable[Mock]:
    with patch("tickit.cli.asyncio.create_task", autospec=True) as mock:
        yield mock


# or just mock out/patch the run_forevers in the components and scheduler to
# just be sleep so nothing happens.
# then we can still await on the sleeps?


def test_scheduler_and_components_included_by_default() -> None:
    tickit_simulation = TickitSimulation("tests/core/sim.yaml")

    assert tickit_simulation._include_components is True
    assert tickit_simulation._include_schedulers is True


def test_backend_internal_by_default() -> None:
    tickit_simulation = TickitSimulation("tests/core/sim.yaml")

    assert tickit_simulation._backend == "internal"


def test_choose_components_to_run() -> None:
    tickit_simulation = TickitSimulation(
        "tests/core/sim.yaml",
        components_to_run="source",
    )
    assert tickit_simulation._components_to_run == "source"


def test_default_includes_all_components() -> None:
    tickit_simulation = TickitSimulation("tests/core/sim.yaml")
    assert (
        tickit_simulation._components_to_run
        == set(tickit_simulation._components.keys())
        == {"source", "sink"}
    )


def test_choosing_all_equivalent_to_choosing_none() -> None:
    tickit_simulation = TickitSimulation(
        "tests/core/sim.yaml",
        components_to_run={"source", "sink"},
    )
    assert tickit_simulation._components_to_run == {"source", "sink"}
    assert tickit_simulation._components_to_run == set(
        tickit_simulation._components.keys()
    )


@pytest.mark.asyncio
async def test_running_only_scheduler(patch_asyncio_create_task) -> None:
    tickit_simulation = TickitSimulation(
        "tests/core/sim.yaml",
        include_components=False,
    )
    assert tickit_simulation._include_components is False
    assert tickit_simulation._include_schedulers is True

    tickit_simulation._start_scheduler_tasks()
    assert tickit_simulation._tasks == patch_asyncio_create_task()
