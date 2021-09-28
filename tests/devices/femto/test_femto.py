import pytest
from mock import Mock, create_autospec

from tickit.core.device import DeviceUpdate
from tickit.core.typedefs import SimTime
from tickit.devices.femto.femto import CurrentDevice, Femto, FemtoAdapter


@pytest.fixture
def femto() -> Femto:
    return Femto()


def test_femto_constructor(femto: Femto):
    pass


def test_set_and_get_gain(femto: Femto):
    femto.set_gain(3.0)
    assert femto.get_gain() == 3.0


def test_set_and_get_current(femto: Femto):
    femto.set_current(3.0)
    assert femto.get_current() == 3.0 * femto.get_gain()


def test_femto_update(femto: Femto):
    device_input = {"input": 3.0}
    time = SimTime(0)
    update: DeviceUpdate = femto.update(time, device_input)
    assert update.outputs["current"] == 3.0 * femto.get_gain()


# # # # # # # # # # CurrentDevice # # # # # # # # # #


@pytest.fixture
def current_device() -> CurrentDevice:
    return CurrentDevice()


def test_current_device_constructor(current_device: CurrentDevice):
    pass


def test_current_device_update(current_device: CurrentDevice):
    time = SimTime(0)
    device_input = {"bleep": "bloop"}
    update: DeviceUpdate = current_device.update(time, device_input)
    assert 0.1 <= update.outputs["output"] <= 200.1


# # # # # # # # # # FemtoAdapter # # # # # # # # # #


@pytest.fixture
def mock_femto() -> Mock:
    return create_autospec(Femto, instance=True)


@pytest.fixture
def raise_interrupt() -> Mock:
    async def raise_interrupt():
        return False

    return Mock(raise_interrupt)


@pytest.fixture
def femto_adapter(mock_femto: Mock, raise_interrupt) -> FemtoAdapter:
    return FemtoAdapter(mock_femto, raise_interrupt)


def test_femto_adapter_constructor(femto_adapter: FemtoAdapter):
    pass


@pytest.mark.asyncio
async def test_run_forever(femto_adapter: FemtoAdapter):
    femto_adapter.build_ioc = Mock(femto_adapter.build_ioc)
    await femto_adapter.run_forever()
    femto_adapter.build_ioc.assert_called_once()


@pytest.mark.asyncio
async def test_femto_adapter_callback(femto_adapter: FemtoAdapter):
    await femto_adapter.callback(2.0)
    femto_adapter._device.set_gain.assert_called_with(2.0)
    femto_adapter.raise_interrupt.assert_called()


def test_on_db_load(femto_adapter: FemtoAdapter):
    femto_adapter.on_db_load()

    input_record = femto_adapter.input_record
    current_record = femto_adapter.current_record
    interrupt_records = femto_adapter.interrupt_records

    assert interrupt_records[input_record] == femto_adapter._device.get_gain
    assert interrupt_records[current_record] == femto_adapter._device.get_current
