"""just a test for me to figure out how this all works..."""

import asyncio
from asyncio import AbstractEventLoop
from dataclasses import dataclass
from typing import List, cast

import mock
import pytest
import pytest_asyncio
from mock import create_autospec

from tickit.core.components.component import Component, ComponentConfig
from tickit.core.components.device_simulation import DeviceSimulation
from tickit.core.device import Device, DeviceUpdate
from tickit.core.management.event_router import Wiring
from tickit.core.management.schedulers.master import MasterScheduler
from tickit.core.state_interfaces.state_interface import get_interface
from tickit.core.typedefs import (
    ComponentException,
    ComponentID,
    ComponentPort,
    PortID,
    SimTime,
)
from tickit.devices.sink import Sink, SinkDevice
from tickit.utils.compat.typing_compat import TypedDict


@dataclass
class Counter(ComponentConfig):
    """Simulation of simple counting device."""

    def __call__(self) -> Component:  # noqa: D102
        return DeviceSimulation(name=self.name, device=CounterDevice())


class CounterDevice(Device):
    Inputs: TypedDict = TypedDict("Inputs", {})
    Outputs: TypedDict = TypedDict("Outputs", {"value": int})

    def __init__(self, initial_value: int = 0, callback_period: int = int(1e9)) -> None:
        self._value = initial_value
        self.callback_period = SimTime(callback_period)

    def update(self, time: SimTime, inputs: Inputs) -> DeviceUpdate[Outputs]:
        self._value = self._value + 1
        return DeviceUpdate(
            CounterDevice.Outputs(value=self._value),
            SimTime(time + self.callback_period),
        )


@pytest.fixture
def component_configs() -> List[ComponentConfig]:
    return [
        Counter(name="counter", inputs={}),
        Sink(
            name="counter_sink",
            inputs={
                PortID("input"): ComponentPort(ComponentID("counter"), PortID("value"))
            },
        ),
    ]


@pytest_asyncio.fixture
async def components(component_configs: List[ComponentConfig]) -> List[Component]:
    return [config() for config in component_configs]


@pytest_asyncio.fixture
async def master_scheduler(components: List[Component], event_loop: AbstractEventLoop):
    wiring = Wiring(
        {
            ComponentID("counter"): {
                PortID("value"): {
                    ComponentPort(ComponentID("counter_sink"), PortID("input"))
                }
            },
            ComponentID("counter_sink"): {},
        }
    )

    with mock.patch(
        "tickit.devices.sink.SinkDevice.update",
        return_value=create_autospec(SinkDevice.update),
    ):
        for component in components:
            event_loop.create_task(component.run_forever(*get_interface("internal")))

        scheduler = MasterScheduler(wiring, *get_interface("internal"))
        assert scheduler.running.is_set() is False

        task = event_loop.create_task(scheduler.run_forever())
        yield scheduler

    exception_future = event_loop.create_task(
        scheduler.handle_component_exception(
            ComponentException(source="sim", error=NotImplementedError, traceback="")
        )
    )
    await asyncio.gather(task, exception_future)
    assert scheduler.running.is_set() is False


@pytest.mark.asyncio
async def test_master_scheduler_is_running(master_scheduler: MasterScheduler):
    await asyncio.wait_for(master_scheduler.running.wait(), timeout=2.0)


@pytest.mark.asyncio
async def test_sink_has_captured_value(
    components: List[Component], master_scheduler: MasterScheduler
):
    sink = cast(DeviceSimulation, components[1])
    assert sink.device_inputs == {}

    await asyncio.wait_for(master_scheduler.ticker.finished.wait(), timeout=2.0)

    sunk_value = master_scheduler.ticker.inputs["counter_sink"]

    mocked_update = cast(mock.MagicMock, sink.device.update)
    mocked_update.assert_called_once_with(0, sunk_value)
    assert sunk_value.get("input") == 1
