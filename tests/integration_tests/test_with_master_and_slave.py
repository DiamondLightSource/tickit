"""just a test for me to figure out how this all works..."""

import asyncio
from asyncio import AbstractEventLoop
from typing import List, Tuple, Union, cast

import mock
import pytest
import pytest_asyncio
from mock import create_autospec

from tickit.core.components.component import Component, ComponentConfig
from tickit.core.components.device_simulation import DeviceSimulation
from tickit.core.components.system_simulation import (
    SystemSimulation,
    SystemSimulationComponent,
)
from tickit.core.management.event_router import InverseWiring, Wiring
from tickit.core.management.schedulers.master import MasterScheduler
from tickit.core.runner import run_all_forever
from tickit.core.state_interfaces.state_interface import get_interface
from tickit.core.typedefs import ComponentException, ComponentID, ComponentPort, PortID
from tickit.devices.sink import Sink, SinkDevice
from tickit.devices.source import Source
from pathlib import Path

from tickit.utils.configuration.loading import read_configs

##IMPLEMENT THIS


@pytest.fixture
def components() -> List[Component]:
    component_configs = [
        Source(name="external_source", inputs={}, value=42),
        SystemSimulation(
            name="internal_tickit",
            inputs={
                PortID("input_1"): ComponentPort(
                    ComponentID("external_source"), PortID("value")
                )
            },
            components=[
                Source(name="internal_source", inputs={}, value=420),
                Sink(
                    name="internal_sink",
                    inputs={
                        PortID("sink_1"): ComponentPort(
                            ComponentID("external"), PortID("input_1")
                        )
                    },
                ),
            ],
            expose={
                PortID("output_1"): ComponentPort(
                    ComponentID("internal_source"), PortID("value")
                )
            },
        ),
        Sink(
            name="external_sink",
            inputs={
                PortID("sink_1"): ComponentPort(
                    ComponentID("internal_tickit"), PortID("output_1")
                )
            },
        ),
    ]
    return [config() for config in component_configs]


@pytest.fixture
def configs_from_yaml() -> List[ComponentConfig]:
    path_to_yaml = Path(__file__).parent / "configs" / "nested.yaml"
    return read_configs(path_to_yaml)


@pytest.fixture(params=["yaml", "not-yaml"])
def wiring_and_components(
    request, configs_from_yaml, components
) -> Tuple[Union[Wiring, InverseWiring], List[Component]]:
    if hasattr(request, "param") and getattr(request, "param") == "yaml":
        return InverseWiring.from_component_configs(configs_from_yaml), [
            config() for config in configs_from_yaml
        ]

    return (
        Wiring(
            {
                ComponentID("external_source"): {
                    PortID("value"): {
                        ComponentPort(ComponentID("internal_tickit"), PortID("input_1"))
                    }
                },
                ComponentID("internal_tickit"): {
                    PortID("output_1"): {
                        ComponentPort(ComponentID("external_sink"), PortID("sink_1"))
                    }
                },
                ComponentID("external_sink"): {},
            }
        ),
        components,
    )


@pytest_asyncio.fixture
async def master_scheduler(
    wiring_and_components: Tuple[Union[Wiring, InverseWiring], List[Component]],
    event_loop: AbstractEventLoop,
):
    wiring, components = wiring_and_components
    # with mock.patch(
    #     "tickit.devices.sink.SinkDevice.update",
    #     return_value=create_autospec(SinkDevice.update),
    # ):
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
    wiring_and_components: Tuple[Union[Wiring, InverseWiring], List[Component]],
    master_scheduler: MasterScheduler,
):
    components = wiring_and_components[1]

    source = cast(DeviceSimulation, components[0])
    sim = cast(SystemSimulationComponent, components[1])
    sink = cast(DeviceSimulation, components[2])
    internal_source = cast(DeviceSimulation, sim.components[0])
    internal_sink = cast(DeviceSimulation, sim.components[1])

    assert sink.device_inputs == internal_sink.device_inputs == {}
    assert source.last_outputs == internal_source.last_outputs == {}

    await master_scheduler.initial_tick.wait()

    # check that the scheduler has scheduled the input changes...
    assert (
        source.last_outputs["value"]
        == sim.scheduler.input_changes["input_1"]
        == internal_sink.device_inputs["sink_1"]
    )

    await asyncio.sleep(0.1)

    source_output_port = "value"
    internal_sink_input_port = "sink_1"

    assert (
        source.last_outputs[source_output_port]
        == internal_sink.device_inputs[internal_sink_input_port]
    )

    # PROBLEM: don't see any output changes to sim.scheduler... my external sink never
    # seems to get the internal source value.
    sunk_value = master_scheduler.ticker.inputs["sink"]

    mocked_update = cast(mock.MagicMock, sink.device.update)
    mocked_update.assert_called_once_with(0, sunk_value)
    assert sunk_value.get("input") == 42
