import asyncio
from typing import Iterable

import pytest
from immutables import Map
from mock import Mock, create_autospec, patch

from tickit.core.adapter import Adapter
from tickit.core.components.device_simulation import DeviceSimulation
from tickit.core.state_interfaces.internal import (
    InternalStateConsumer,
    InternalStateProducer,
    InternalStateServer,
)
from tickit.core.typedefs import Changes, ComponentID, Output, PortID, SimTime
from tickit.devices.source import Source, SourceDevice


@pytest.fixture
def source() -> SourceDevice:
    source = SourceDevice(value=42)
    return source


@pytest.fixture
def mock_adapter() -> Mock:
    return create_autospec(Adapter)


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
def patch_asyncio_wait() -> Iterable[Mock]:
    with patch(
        "tickit.core.components.device_simulation.asyncio.wait", autospec=True
    ) as mock:
        yield mock


@pytest.fixture
def patch_run_all() -> Iterable[Mock]:
    with patch(
        "tickit.core.components.device_simulation.run_all", autospec=True
    ) as mock:
        mock.return_value = asyncio.create_task(asyncio.sleep(0))
        yield mock


@pytest.fixture
def device_simulation(
    source: Source,
    mock_adapter: Adapter,
) -> DeviceSimulation:
    return DeviceSimulation(
        name=ComponentID("test_device_simulation"),
        device=source,
        adapters=[mock_adapter],
    )


def test_device_simulation_constructor(device_simulation: DeviceSimulation):
    pass


@pytest.mark.asyncio
async def test_device_simulation_run_forever_method(
    device_simulation: DeviceSimulation,
    mock_state_producer: Mock,
    mock_state_consumer: Mock,
    patch_asyncio_wait: Mock,
):
    with patch(
        "tickit.core.components.device_simulation.run_all", autospec=True
    ) as mock_all:
        mock_all.return_value = [asyncio.create_task(asyncio.sleep(0))]
        await device_simulation.run_forever(mock_state_consumer, mock_state_producer)
        patch_asyncio_wait.assert_awaited_once_with(
            mock_all.return_value, return_when=asyncio.FIRST_COMPLETED
        )

    changes = Changes(Map({PortID("foo"): 43}))
    await device_simulation.on_tick(SimTime(1), changes)

    device_simulation.adapters[0].after_update.assert_called_once()  # type: ignore
    assert device_simulation.last_outputs == {"value": 42}
    device_simulation.state_producer.produce.assert_awaited_once_with(  # type: ignore
        "tickit-test_device_simulation-out",
        Output(
            source=ComponentID("test_device_simulation"),
            time=SimTime(1),
            changes=Map({"value": 42}),  # type: ignore
            call_at=None,
        ),
    )
