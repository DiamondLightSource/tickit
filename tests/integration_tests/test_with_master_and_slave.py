"""just a test for me to figure out how this all works..."""

import asyncio
from asyncio import AbstractEventLoop
from pathlib import Path
from typing import List, cast

import pytest
import pytest_asyncio

from tickit.core.components.component import Component, ComponentConfig
from tickit.core.components.device_simulation import DeviceSimulation
from tickit.core.components.system_simulation import SystemSimulationComponent
from tickit.core.management.event_router import InverseWiring
from tickit.core.management.schedulers.master import MasterScheduler
from tickit.core.runner import run_all_forever
from tickit.core.state_interfaces.state_interface import get_interface
from tickit.core.typedefs import ComponentException
from tickit.utils.configuration.loading import read_configs


@pytest.fixture
def configs_from_yaml() -> List[ComponentConfig]:
    path_to_yaml = Path(__file__).parent / "configs" / "nested.yaml"
    return read_configs(path_to_yaml)


@pytest.fixture
def wiring(configs_from_yaml) -> InverseWiring:
    return InverseWiring.from_component_configs(configs_from_yaml)


@pytest.fixture
def components(configs_from_yaml) -> List[Component]:
    return [config() for config in configs_from_yaml]


@pytest_asyncio.fixture
async def master_scheduler(
    wiring: InverseWiring,
    components: List[Component],
    event_loop: AbstractEventLoop,
):
    scheduler = MasterScheduler(wiring, *get_interface("internal"))

    assert scheduler.running.is_set() is False
    run_task = event_loop.create_task(
        run_all_forever(
            [
                component.run_forever(*get_interface("internal"))
                for component in components
            ]
            + [scheduler.run_forever()]
        )
    )

    yield scheduler

    exception_task = event_loop.create_task(
        scheduler.handle_component_exception(
            ComponentException(source="sim", error=NotImplementedError, traceback="")
        )
    )

    await asyncio.gather(run_task, exception_task)
    assert scheduler.running.is_set() is False


@pytest.mark.asyncio
async def test_master_scheduler_is_running(master_scheduler: MasterScheduler):
    await asyncio.wait_for(master_scheduler.running.wait(), timeout=2.0)


@pytest.mark.asyncio
async def test_sink_has_captured_value(
    components: List[Component],
    master_scheduler: MasterScheduler,
):
    source = cast(DeviceSimulation, components[0])
    sim = cast(SystemSimulationComponent, components[1])
    sink = cast(DeviceSimulation, components[2])

    assert sink.device_inputs == {}
    assert source.last_outputs == {}

    await asyncio.wait_for(master_scheduler.ticker.finished.wait(), timeout=3.0)

    assert source.last_outputs["value"] == sim.scheduler.input_changes["input_1"]
