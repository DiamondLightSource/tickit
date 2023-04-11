import asyncio
from typing import AsyncGenerator, Iterable

import pytest
from immutables import Map
from mock import AsyncMock, Mock, create_autospec, patch

from tickit.core.adapter import Adapter
from tickit.core.components.device_simulation import DeviceSimulation
from tickit.core.state_interfaces.state_interface import StateConsumer, StateProducer
from tickit.core.typedefs import (
    Changes,
    ComponentID,
    Input,
    Output,
    PortID,
    SimTime,
    StopComponent,
)
from tickit.devices.source import SourceDevice


@pytest.fixture
def source() -> SourceDevice:
    source = SourceDevice(value=42)
    return source


@pytest.fixture
def mock_adapter() -> Mock:
    return create_autospec(Adapter)


@pytest.fixture
def mock_state_producer_type() -> Mock:
    mock: Mock = create_autospec(StateProducer, instance=False)
    mock.return_value = create_autospec(StateProducer, instance=True)
    return mock


@pytest.fixture
def mock_state_consumer_type() -> Mock:
    return create_autospec(StateConsumer, instance=False)


@pytest.fixture
def patch_asyncio_wait() -> Iterable[Mock]:
    with patch(
        "tickit.core.components.device_simulation.asyncio.wait", autospec=True
    ) as mock:
        yield mock


@pytest.fixture
async def patch_run_all() -> AsyncGenerator[Mock, None]:
    with patch(
        "tickit.core.components.device_simulation.run_all", autospec=True
    ) as mock:
        mock.return_value = [asyncio.create_task(asyncio.sleep(0))]
        yield mock


@pytest.fixture
def device_simulation(
    source: SourceDevice,
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
    mock_state_producer_type: Mock,
    mock_state_consumer_type: Mock,
    patch_asyncio_wait: Mock,
):
    with patch(
        "tickit.core.components.device_simulation.run_all", autospec=True
    ) as mock_all:
        mock_all.return_value = [asyncio.create_task(asyncio.sleep(0))]
        await device_simulation.run_forever(
            mock_state_consumer_type, mock_state_producer_type
        )
        patch_asyncio_wait.assert_awaited_once_with(mock_all.return_value)

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


@pytest.mark.asyncio
async def test_device_simulation_handles_exception_in_handle_input(
    device_simulation: DeviceSimulation,
    mock_state_producer_type: Mock,
    mock_state_consumer_type: Mock,
):
    await device_simulation.run_forever(
        mock_state_consumer_type, mock_state_producer_type  # type: ignore
    )

    def raise_error(time, changes):
        raise RuntimeError("Test exception")

    device_simulation.on_tick = AsyncMock()  # type: ignore
    device_simulation.on_tick.side_effect = raise_error
    await device_simulation.handle_input(
        Input(ComponentID("Test"), SimTime(42), Changes(Map()))
    )
    device_simulation.on_tick.assert_awaited_once_with(SimTime(42), Changes(Map()))
    device_simulation.state_producer.produce.assert_awaited_once()  # type: ignore


@pytest.mark.asyncio
async def test_device_simulation_stops_when_told(
    device_simulation: DeviceSimulation,
    mock_state_producer_type: Mock,
    mock_state_consumer_type: Mock,
):
    await device_simulation.run_forever(
        mock_state_consumer_type, mock_state_producer_type  # type: ignore
    )

    await device_simulation.handle_input(StopComponent())
    assert all(map(lambda task: task.done(), device_simulation._tasks))
