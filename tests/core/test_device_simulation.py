from typing import Hashable, Iterable, Mapping, cast

import pytest
from immutables import Map
from mock import Mock, create_autospec, patch

from tickit.core.adapter import AdapterConfig, ListeningAdapter
from tickit.core.components.device_simulation import DeviceSimulation
from tickit.core.state_interfaces.internal import (
    InternalStateConsumer,
    InternalStateProducer,
    InternalStateServer,
)
from tickit.core.typedefs import Changes, ComponentID, PortID, SimTime
from tickit.devices.source import Source


@pytest.fixture
def source() -> Source:
    source = Source(value=42)
    return source


@pytest.fixture
def mock_adapter() -> Mock:
    return create_autospec(AdapterConfig)


@pytest.fixture
def mock_server() -> Mock:
    return create_autospec(InternalStateServer, instance=True)


@pytest.fixture
def mock_state_producer(mock_server: Mock) -> Mock:
    mock: Mock = create_autospec(InternalStateProducer, instance=False)
    mock.return_value = create_autospec(InternalStateProducer, instance=True)
    mock.return_value.server = mock_server
    return mock


@pytest.fixture
def mock_state_consumer() -> Mock:
    return create_autospec(InternalStateConsumer, instance=False)


@pytest.fixture
def patch_asyncio() -> Iterable[Mock]:
    with patch(
        "tickit.core.components.device_simulation.asyncio", autospec=True
    ) as mock:
        yield mock


@pytest.fixture
def device_simulation(
    source: Source,
    mock_adapter: AdapterConfig,
    mock_state_producer: Mock,
    mock_state_consumer: Mock,
) -> DeviceSimulation:
    return DeviceSimulation(
        name=ComponentID("test_device_simulation"),
        state_consumer=mock_state_consumer,
        state_producer=mock_state_producer,
        device=source.SourceConfig(42),
        adapters=[mock_adapter],
    )


def test_device_simulation_constructor(device_simulation: DeviceSimulation):
    pass


@pytest.mark.asyncio
async def test_device_simulation_run_forever_method(
    device_simulation: DeviceSimulation,
    patch_asyncio: Mock,
):
    assert not hasattr(device_simulation, "state_producer")
    assert not hasattr(device_simulation, "state_consumer")

    await device_simulation.run_forever()

    assert hasattr(device_simulation, "state_producer")
    assert hasattr(device_simulation, "state_consumer")

    assert isinstance(device_simulation.state_consumer, InternalStateConsumer)
    assert isinstance(device_simulation.state_producer, InternalStateProducer)

    mock_asyncio: Mock = patch_asyncio
    assert mock_asyncio.wait.call_count == 1


@pytest.mark.asyncio
async def test_device_simulation_on_tick_method(device_simulation: DeviceSimulation):
    assert not hasattr(device_simulation, "state_producer")
    assert not hasattr(device_simulation, "state_consumer")

    await device_simulation.set_up_state_interfaces()

    assert hasattr(device_simulation, "state_producer")
    assert hasattr(device_simulation, "state_consumer")

    changes: Map[PortID, Hashable] = Map({PortID("42"): 42})

    assert device_simulation.device_inputs == {}

    await device_simulation.on_tick(SimTime(0), Changes(changes))

    assert device_simulation.device_inputs == {**cast(Mapping[str, Hashable], changes)}

    for adapter in device_simulation.adapters:
        if isinstance(adapter, ListeningAdapter):
            adapter.after_update.assert_called_once()  # type: ignore

    assert device_simulation.last_outputs == {"value": 42}
    device_simulation.state_producer.server.push.assert_called_once()  # type: ignore
