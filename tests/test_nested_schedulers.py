"""just a test for me to figure out how this all works..."""

import asyncio
from asyncio import AbstractEventLoop
from dataclasses import dataclass
from typing import Any, Dict, List, TypedDict, cast

import aiomonitor
import pytest
import pytest_asyncio

# need a list of components here... ComponentConfigs.
from tickit.core.components.component import Component, ComponentConfig
from tickit.core.components.device_simulation import DeviceSimulation
from tickit.core.components.system_simulation import (
    SystemSimulation,
    SystemSimulationComponent,
)
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


class SinkDevice(Device):
    """A simple device which stores its sunk value."""

    Inputs: TypedDict = TypedDict("Inputs", {"input": Any})
    Outputs: TypedDict = TypedDict("Outputs", {})

    def update(self, time: SimTime, inputs: Inputs) -> DeviceUpdate[Outputs]:
        self.sunk_value = inputs["input"]
        return DeviceUpdate(SinkDevice.Outputs(), None)


class Sink(ComponentConfig):
    """Arbitrary value sink that logs the value."""

    def __call__(self) -> Component:  # noqa: D102
        return DeviceSimulation(
            name=self.name,
            device=SinkDevice(),
        )


@dataclass
class Counter(ComponentConfig):
    """Simulation of simple counting device."""

    def __call__(self) -> Component:  # noqa: D102
        return DeviceSimulation(name=self.name, device=CounterDevice())


class CounterDevice(Device):
    """A simple device which increments a value."""

    #: An empty typed mapping of input values
    Inputs: TypedDict = TypedDict("Inputs", {})
    #: A typed mapping containing the 'value' output value
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


@pytest.fixture
def system_simulation(
    component_configs: List[ComponentConfig],
) -> SystemSimulationComponent:
    expose_ports: Dict[PortID, ComponentPort] = {
        PortID("value"): ComponentPort(ComponentID("counter"), PortID("value"))
    }
    return SystemSimulation("sim", {}, component_configs, expose_ports)()


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


@pytest_asyncio.fixture
async def tickit_in_tickit(
    system_simulation: SystemSimulationComponent, event_loop: AbstractEventLoop
):
    wiring: Wiring = Wiring({ComponentID("sim"): {PortID("value"): {}}})

    event_loop.create_task(system_simulation.run_forever(*get_interface("internal")))
    scheduler = MasterScheduler(wiring, *get_interface("internal"))

    assert scheduler.running.is_set() is False
    # assert len(system_simulation.components) != 0

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

    sunk_value = master_scheduler.ticker.inputs["counter_sink"].get("input")
    sink_device = cast(SinkDevice, sink.device)

    assert sunk_value == sink_device.sunk_value


# now lets make it work for a SystemSimulation...
@pytest.mark.asyncio
async def test_system_simulation(
    system_simulation: SystemSimulationComponent, tickit_in_tickit: MasterScheduler
):
    # test that the scheduler (slave) is doing it's job properly, and that the components
    # in those are correctly being updated...
    await asyncio.wait_for(tickit_in_tickit.ticker.finished.wait(), timeout=2.0)
    sink = cast(DeviceSimulation, system_simulation.components[1])
    assert sink.device_inputs == {}

    await asyncio.wait_for(
        system_simulation.scheduler.ticker.finished.wait(), timeout=5
    )

    print("ah")
