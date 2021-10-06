from typing import Awaitable, Callable

import pytest
from mock import Mock, create_autospec

from tickit.core.device import DeviceUpdate
from tickit.core.typedefs import SimTime
from tickit.devices.pneumatic.pneumatic import Pneumatic, PneumaticAdapter


@pytest.fixture
def pneumatic() -> Pneumatic:
    return Pneumatic()


def test_pneumatic_constructor(pneumatic: Pneumatic):
    pass


def test_pneumatic_set_and_get_speed(pneumatic: Pneumatic):
    pneumatic.set_speed(3.0)
    assert pneumatic.get_speed() == 3.0


def test_pneumatic_set_and_get_state(pneumatic: Pneumatic):
    initial_state = pneumatic.get_state()
    pneumatic.set_state()
    assert pneumatic.target_state is not initial_state


def test_pneumatic_update(pneumatic: Pneumatic):
    time = SimTime(0)
    initial_state = pneumatic.get_state()
    pneumatic.set_state()
    device_update: DeviceUpdate = pneumatic.update(time, {})

    assert device_update.outputs["output"] is not initial_state


def test_pneumatic_update_no_state_change(pneumatic: Pneumatic):
    time = SimTime(0)
    initial_state = pneumatic.get_state()
    device_update: DeviceUpdate = pneumatic.update(time, {})

    assert device_update.outputs["output"] is initial_state


# # # # # # # # # # PneumaticAdapter # # # # # # # # # #


@pytest.fixture
def mock_pneumatic() -> Mock:
    return create_autospec(Pneumatic)


@pytest.fixture
def raise_interrupt() -> Mock:
    async def raise_interrupt():
        return False

    return Mock(raise_interrupt)


@pytest.fixture
def pneumatic_adapter(mock_pneumatic: Mock, raise_interrupt: Mock) -> PneumaticAdapter:
    return PneumaticAdapter(mock_pneumatic, raise_interrupt, "data.db")


def test_pneumatic_adapter_constructor(pneumatic_adapter: PneumaticAdapter):
    pass


class FalsePneumaticAdapter(PneumaticAdapter):
    def __init__(
        self,
        device: Pneumatic,
        raise_interrupt: Callable[[], Awaitable[None]],
        db_file: str,
    ):
        self.times_build_ioc_called = 0
        super().__init__(device, raise_interrupt, db_file)

    def build_ioc(self) -> None:
        self.times_build_ioc_called += 1

    def get_times_build_ioc_called(self) -> int:
        return self.times_build_ioc_called


@pytest.fixture
def false_pneumatic_adapter(mock_pneumatic, raise_interrupt) -> FalsePneumaticAdapter:
    return FalsePneumaticAdapter(mock_pneumatic, raise_interrupt, "data.db")


@pytest.mark.asyncio
async def test_pneumatic_adapter_run_forever(false_pneumatic_adapter: PneumaticAdapter):
    await false_pneumatic_adapter.run_forever()
    assert false_pneumatic_adapter.get_times_build_ioc_called() == 1


@pytest.mark.asyncio
async def test_pneumatic_adapter_callback(pneumatic_adapter: PneumaticAdapter):
    await pneumatic_adapter.callback(None)
    pneumatic_adapter._device.set_state.assert_called_once()
    pneumatic_adapter.raise_interrupt.assert_awaited_once_with()


def test_pneumatic_adapter_on_db_load(pneumatic_adapter: PneumaticAdapter):
    pneumatic_adapter.on_db_load()
