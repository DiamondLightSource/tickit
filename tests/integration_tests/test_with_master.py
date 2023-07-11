"""just a test for me to figure out how this all works..."""

import asyncio
from asyncio import AbstractEventLoop
from pathlib import Path
from typing import List, Tuple, Union, cast

import mock
import pytest
import pytest_asyncio
from mock import create_autospec

from tickit.core.components.component import Component, ComponentConfig
from tickit.core.components.device_simulation import DeviceSimulation
from tickit.core.management.event_router import InverseWiring, Wiring
from tickit.core.management.schedulers.master import MasterScheduler
from tickit.core.runner import run_all_forever
from tickit.core.state_interfaces.state_interface import get_interface
from tickit.core.typedefs import ComponentException, ComponentID, ComponentPort, PortID
from tickit.devices.sink import Sink, SinkDevice
from tickit.devices.source import Source
from tickit.utils.configuration.loading import read_configs


@pytest.fixture
def configs_from_yaml() -> List[ComponentConfig]:
    path_to_yaml = Path(__file__).parent / "configs" / "test_with_master.yaml"
    return read_configs(path_to_yaml)


@pytest.fixture
def wiring(configs_from_yaml: List[ComponentConfig]) -> InverseWiring:
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
    with mock.patch(
        "tickit.devices.sink.SinkDevice.update",
        return_value=create_autospec(SinkDevice.update),
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
    sink = cast(DeviceSimulation, components[1])
    assert sink.device_inputs == {}

    await asyncio.wait_for(master_scheduler.ticker.finished.wait(), timeout=2.0)

    sunk_value = master_scheduler.ticker.inputs["sink"]

    mocked_update = cast(mock.MagicMock, sink.device.update)
    mocked_update.assert_called_once_with(0, sunk_value)
    assert sunk_value.get("input") == 42
