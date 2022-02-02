import asyncio

import pytest
from aioca import caget, caput

from tickit.core.device import DeviceUpdate
from tickit.core.typedefs import SimTime
from tickit.devices.femto.current import CurrentDevice
from tickit.devices.femto.femto import FemtoDevice


@pytest.fixture
def femto() -> FemtoDevice:
    return FemtoDevice(initial_gain=2.5, initial_current=0.0)


def test_femto_constructor(femto: FemtoDevice):
    pass


def test_set_and_get_gain(femto: FemtoDevice):
    femto.set_gain(3.0)
    assert femto.get_gain() == 3.0


def test_set_and_get_current(femto: FemtoDevice):
    femto.set_current(3.0)
    assert femto.get_current() == 3.0 * femto.get_gain()


def test_femto_update(femto: FemtoDevice):
    device_input: FemtoDevice.Inputs = {"input": 3.0}
    time = SimTime(0)
    update: DeviceUpdate = femto.update(time, device_input)
    assert update.outputs["current"] == 3.0 * femto.get_gain()


# # # # # # # # # # CurrentDevice # # # # # # # # # #


@pytest.fixture
def current_device() -> CurrentDevice:
    return CurrentDevice(callback_period=1000000000)


def test_current_device_constructor(current_device: CurrentDevice):
    pass


def test_current_device_update(current_device: CurrentDevice):
    time = SimTime(0)
    device_input = {"bleep": "bloop"}
    update: DeviceUpdate = current_device.update(time, device_input)
    assert 100 <= update.outputs["output"] < 200


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "tickit_process", ["examples/configs/current-monitor.yaml"], indirect=True
)
async def test_femto_system(tickit_process):
    assert (await caget("FEMTO:GAIN_RBV")) == 2.5
    current = await caget("FEMTO:CURRENT")
    assert 100 * 2.5 <= current < 200 * 2.5
    await caput("FEMTO:GAIN", 0.01)
    await asyncio.sleep(0.5)
    assert (await caget("FEMTO:GAIN_RBV")) == 0.01
    current = await caget("FEMTO:CURRENT")
    assert 100 * 0.01 <= current < 200 * 0.01
