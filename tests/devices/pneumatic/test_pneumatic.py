import asyncio

import pytest
from aioca import caget, caput

from tickit.core.device import DeviceUpdate
from tickit.core.typedefs import SimTime
from tickit.devices.pneumatic.pneumatic import PneumaticDevice


@pytest.fixture
def pneumatic() -> PneumaticDevice:
    return PneumaticDevice(initial_speed=0.5, initial_state=False)


def test_pneumatic_constructor(pneumatic: PneumaticDevice):
    pass


def test_pneumatic_set_and_get_speed(pneumatic: PneumaticDevice):
    pneumatic.set_speed(3.0)
    assert pneumatic.get_speed() == 3.0


def test_pneumatic_set_and_get_state(pneumatic: PneumaticDevice):
    initial_state = pneumatic.get_state()
    pneumatic.set_state()
    assert pneumatic.target_state is not initial_state


def test_pneumatic_update(pneumatic: PneumaticDevice):
    time = SimTime(0)
    initial_state = pneumatic.get_state()
    pneumatic.set_state()
    device_update: DeviceUpdate = pneumatic.update(time, {})

    assert device_update.outputs["output"] is not initial_state


def test_pneumatic_update_no_state_change(pneumatic: PneumaticDevice):
    time = SimTime(0)
    initial_state = pneumatic.get_state()
    device_update: DeviceUpdate = pneumatic.update(time, {})

    assert device_update.outputs["output"] is initial_state


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "tickit_process", ["examples/configs/attns.yaml"], indirect=True
)
async def test_pneumatic_system(tickit_process):
    async def toggle(expected: bool):
        assert (await caget("PNEUMATIC:FILTER_RBV")) != expected
        await caput("PNEUMATIC:FILTER", expected)
        await asyncio.sleep(0.8)
        assert (await caget("PNEUMATIC:FILTER_RBV")) == expected

    await toggle(True)
    await toggle(False)
