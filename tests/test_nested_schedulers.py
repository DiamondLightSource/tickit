import asyncio
from asyncio import AbstractEventLoop
from dataclasses import dataclass
from typing import Dict, List, Tuple, cast

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
from tickit.core.device import Device, DeviceUpdate
from tickit.core.management.event_router import InverseWiring, Wiring
from tickit.core.management.schedulers.master import MasterScheduler
from tickit.core.runner import run_all_forever
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
def internal_component_configs() -> List[ComponentConfig]:
    return [
        Counter(name="internal_counter", inputs={}),
        Sink(
            name="internal_counter_sink",
            inputs={
                PortID("input"): ComponentPort(
                    ComponentID("internal_counter"), PortID("value")
                )
            },
        ),
    ]


@pytest.fixture
def internal_components(
    internal_component_configs: List[ComponentConfig],
) -> List[Component]:
    return [config() for config in internal_component_configs]


@pytest.fixture
def external_component_configs(
    internal_component_configs: List[ComponentConfig],
) -> List[ComponentConfig]:
    input_ports: Dict[PortID, ComponentPort] = {
        PortID("input"): ComponentPort(ComponentID("external_counter"), PortID("value"))
    }
    expose: Dict[PortID, ComponentPort] = {
        PortID("output"): ComponentPort(
            ComponentID("internal_counter"), PortID("value")
        )
    }

    return [
        Counter(name="external_counter", inputs={}),
        SystemSimulation(
            name="sim",
            inputs=input_ports,
            components=internal_component_configs,
            expose=expose,
        ),
        Sink(
            name="external_sink",
            inputs={
                PortID("input"): ComponentPort(ComponentID("sim"), PortID("output"))
            },
        ),
    ]


@pytest.fixture
def external_components(
    external_component_configs: List[ComponentConfig],
) -> List[Component]:
    return [config() for config in external_component_configs]


@pytest_asyncio.fixture
async def master_scheduler(
    internal_component_configs: List[ComponentConfig],
    external_component_configs: List[ComponentConfig],
    external_components: List[Component],
    event_loop: AbstractEventLoop,
):
    wiring: Wiring = Wiring(
        {
            ComponentID("external_counter"): {
                PortID("value"): {ComponentPort(ComponentID("sim"), PortID("input"))}
            },
            ComponentID("sim"): {
                PortID("output"): {
                    ComponentPort(ComponentID("external_sink"), PortID("input"))
                }
            },
            ComponentID("external_sink"): {},
        }
    )
    scheduler = MasterScheduler(wiring, *get_interface("internal"))

    with mock.patch(
        "tickit.devices.sink.SinkDevice.update",
        return_value=create_autospec(SinkDevice.update),
    ):
        assert scheduler.running.is_set() is False
        run_task = event_loop.create_task(
            run_all_forever(
                [
                    component.run_forever(*get_interface("internal"))
                    for component in external_components
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


# now lets make it work for a SystemSimulation...
@pytest.mark.asyncio
async def test_system_simulation(
    external_components: List[Component],
    internal_components: List[Component],
    master_scheduler: MasterScheduler,
):
    internal_sink = cast(DeviceSimulation, internal_components[1])
    system_simulation = cast(SystemSimulationComponent, external_components[1])
    external_counter = cast(DeviceSimulation, external_components[0])
    external_sink = cast(DeviceSimulation, external_components[2])

    # checks to make before the master's first tick.
    assert internal_sink.device_inputs == {}

    await master_scheduler.ticker.finished.wait()

    # checks to make after the master's first tick (but before slaves)
    sim_input = master_scheduler.ticker.inputs["sim"]
    external_counter_value = master_scheduler.ticker.inputs["external_counter"]

    assert sim_input and not external_counter_value
    assert external_counter.last_outputs == {"value": 1}
    assert sim_input == {"input": 1}

    await system_simulation.scheduler.ticker.finished.wait()

    # wait for the external sink to register an input value,
    # while not external_sink.device_inputs:
    #     await asyncio.sleep(TEST_TIME * 1e-9 / 2)
    # # wait for the internal sink to have an input value.

    print("ah")
    # checks to make after the slave's first tick.

    print("ah")


from pathlib import Path
from tickit.utils.configuration.loading import read_configs

TEST_TIME = int(1e9)


@pytest.fixture
def configs_from_yaml() -> List[ComponentConfig]:
    path_to_yaml = Path(__file__).parent.parent / "examples" / "configs" / "nested.yaml"
    configs = read_configs(path_to_yaml)

    for config in configs:
        if hasattr(config, "callback_period"):
            setattr(config, "callback_period", TEST_TIME)

    return configs


@pytest.fixture
def components_from_configs(
    configs_from_yaml: List[ComponentConfig],
) -> List[Component]:
    return [config() for config in configs_from_yaml]


@pytest.fixture
def inverse_wiring(configs_from_yaml: List[ComponentConfig]) -> InverseWiring:
    return InverseWiring.from_component_configs(configs_from_yaml)


@pytest_asyncio.fixture
async def setup_scheduler(
    inverse_wiring: InverseWiring,
    components_from_configs: List[Component],
    event_loop: AbstractEventLoop,
):
    scheduler = MasterScheduler(inverse_wiring, *get_interface("internal"))

    assert scheduler.running.is_set() is False
    run_task = event_loop.create_task(
        run_all_forever(
            [
                component.run_forever(*get_interface("internal"))
                for component in components_from_configs
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


import socket


@pytest.mark.asyncio
async def test_system_simulation_2(
    components_from_configs: List[Component],
    inverse_wiring: InverseWiring,
    setup_scheduler: MasterScheduler,
):
    trampoline = cast(DeviceSimulation, components_from_configs[0])
    sim = cast(SystemSimulationComponent, components_from_configs[1])
    sink = cast(DeviceSimulation, components_from_configs[2])

    internal_sink = cast(DeviceSimulation, sim.components[0])
    internal_rc = cast(DeviceSimulation, sim.components[1])

    sim_inputs = inverse_wiring[sim.name]
    sim_input_port = list(sim_inputs.keys())[0]
    trampoline_output_port = list(sim_inputs.values())[0].port

    await setup_scheduler.ticker.finished.wait()

    sim_input_value = setup_scheduler.ticker.inputs[sim.name][sim_input_port]
    trampoline_output_value = trampoline.last_outputs[trampoline_output_port]

    assert sim_input_value == trampoline_output_value

    # wait for the internal sink to register an input value,
    while not internal_sink.device_inputs:
        await asyncio.sleep(TEST_TIME * 1e-9 / 2)

    assert list(internal_sink.device_inputs.values())[0] == sim_input_value

    await sim.scheduler.ticker.finished.wait()
    # set the observed value of the rc,

    # wait for the server to be up,
    # await internal_rc.adapters[0].server.up.wait()

    # # send data over the tcp socket
    # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # s.connect(("localhost", 25565))
    # s.send(b"O=23")
    # s.close()

    # # wait for the external sink to register an input value,
    # while not sink.device_inputs:
    #     await asyncio.sleep(TEST_TIME * 1e-9 / 2)
    # # wait for the internal sink to have an input value.

    print("ah")
