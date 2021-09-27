import logging
import struct
from typing import Optional

import numpy as np
import pytest
from mock import Mock
from mock.mock import create_autospec

from tickit.core.device import DeviceUpdate
from tickit.core.typedefs import SimTime
from tickit.devices.cryostream.cryostream import Cryostream, CryostreamAdapter
from tickit.devices.cryostream.states import PhaseIds

# # # # # Cryostream Tests # # # # #


@pytest.fixture
def cryostream() -> Cryostream:
    return Cryostream()


def test_cryostream_constructor():
    Cryostream()


def test_cryostream_update_hold(cryostream):
    starting_temperature = cryostream.gas_temp
    device_update: DeviceUpdate = cryostream.update(time=SimTime(1e9), inputs={})
    device_update.outputs["temperature"] == starting_temperature


@pytest.mark.asyncio
async def test_cryostream_update_cool(cryostream: Cryostream):
    starting_temperature = cryostream.gas_temp
    target_temperature = starting_temperature - 50
    await cryostream.cool(target_temperature)

    time = SimTime(0)
    device_update: DeviceUpdate
    while cryostream.phase_id != PhaseIds.HOLD.value:
        logging.info(f"Running time step: {time}")
        device_update = cryostream.update(time, inputs={})
        time_update: Optional[SimTime] = device_update.call_at

        if time_update is None:
            time = SimTime(int(time) + int(1e9))
            continue
        else:
            time = time_update

    max_diff = 10
    margin_of_error = np.array([+max_diff, -max_diff])
    assert any(
        (device_update.outputs["temperature"] + margin_of_error) == target_temperature
    )


@pytest.mark.asyncio
async def test_cryostream_update_end(cryostream: Cryostream):
    starting_temperature = cryostream.default_temp_shutdown - 100
    cryostream.gas_temp = starting_temperature
    await cryostream.end(cryostream.default_ramp_rate)
    assert cryostream.phase_id == PhaseIds.RAMP.value
    assert cryostream.gas_flow == 10

    time = SimTime(0)
    device_update: DeviceUpdate
    while cryostream.phase_id != PhaseIds.HOLD.value:
        logging.info(f"Running time step: {time}")
        device_update = cryostream.update(time, inputs={})
        time_update: Optional[SimTime] = device_update.call_at

        if time_update is None:
            # time = SimTime(int(time) + int(1e9))
            continue
        else:
            time = time_update

    assert device_update.outputs["temperature"] == cryostream.default_temp_shutdown


# # # # # CryostreamAdapter Tests # # # # #


@pytest.fixture
def mock_cryostream() -> Mock:
    return create_autospec(Cryostream, instance=True)


@pytest.fixture
def raise_interrupt():
    async def raise_interrupt():
        return False

    return Mock(raise_interrupt)


@pytest.fixture
def cryostream_adapter(mock_cryostream):
    return CryostreamAdapter(
        mock_cryostream, raise_interrupt, host="localhost", port=25565
    )


def test_cryostream_adapter_constructor():
    CryostreamAdapter(mock_cryostream, raise_interrupt, host="localhost", port=25565)


@pytest.mark.asyncio
async def test_cryostream_adapter_on_connect_gets_device_status(
    cryostream_adapter: CryostreamAdapter,
):
    await cryostream_adapter.on_connect().__anext__()
    device: Mock = cryostream_adapter._device
    device.get_status.assert_called_with(1)


@pytest.mark.asyncio
async def test_cryostream_adapter_restart(cryostream_adapter):
    await cryostream_adapter.restart()
    device: Mock = cryostream_adapter._device
    device.restart.assert_called()


@pytest.mark.asyncio
async def test_cryostream_adapter_hold(cryostream_adapter: CryostreamAdapter):
    await cryostream_adapter.hold()
    device: Mock = cryostream_adapter._device
    device.hold.assert_called()


@pytest.mark.asyncio
async def test_cryostream_adapter_purge(cryostream_adapter: CryostreamAdapter):
    await cryostream_adapter.purge()
    device: Mock = cryostream_adapter._device
    device.purge.assert_called()


@pytest.mark.asyncio
async def test_cryostream_adapter_pause(cryostream_adapter: CryostreamAdapter):
    await cryostream_adapter.pause()
    device: Mock = cryostream_adapter._device
    device.pause.assert_called()


@pytest.mark.asyncio
async def test_cryostream_adapter_resume(cryostream_adapter: CryostreamAdapter):
    await cryostream_adapter.resume()
    device: Mock = cryostream_adapter._device
    device.resume.assert_called()


@pytest.mark.asyncio
async def test_cryostream_adapter_stop(cryostream_adapter: CryostreamAdapter):
    await cryostream_adapter.stop()
    device: Mock = cryostream_adapter._device
    device.stop.assert_called()


@pytest.mark.asyncio
async def test_cryostream_adapter_turbo(cryostream_adapter: CryostreamAdapter):
    await cryostream_adapter.turbo((1).to_bytes(1, byteorder="big"))
    device: Mock = cryostream_adapter._device
    device.turbo.assert_called_with(1)


@pytest.mark.asyncio
async def test_cryostream_adapter_set_status_format(
    cryostream_adapter: CryostreamAdapter,
):
    await cryostream_adapter.set_status_format((1).to_bytes(1, byteorder="big"))
    device: Mock = cryostream_adapter._device
    device.set_status_format.assert_called_with(1)


@pytest.mark.asyncio
async def test_cryostream_adapter_plat(
    cryostream_adapter: CryostreamAdapter,
):
    await cryostream_adapter.plat((1).to_bytes(2, byteorder="big"))
    device: Mock = cryostream_adapter._device
    device.plat.assert_called_with(1)


@pytest.mark.asyncio
async def test_cryostream_adapter_end(
    cryostream_adapter: CryostreamAdapter,
):
    await cryostream_adapter.end((360).to_bytes(2, byteorder="big"))
    device: Mock = cryostream_adapter._device
    device.end.assert_called_with(360)


@pytest.mark.asyncio
async def test_cryostream_adapter_cool(
    cryostream_adapter: CryostreamAdapter,
):
    await cryostream_adapter.cool((300).to_bytes(2, byteorder="big"))
    device: Mock = cryostream_adapter._device
    device.cool.assert_called_with(300)


@pytest.mark.asyncio
async def test_cryostream_adapter_ramp(
    cryostream_adapter: CryostreamAdapter,
):
    values = struct.pack(">HH", 360, 1000)
    await cryostream_adapter.ramp(values)
    device: Mock = cryostream_adapter._device
    device.ramp.assert_called_with(360, 1000)
