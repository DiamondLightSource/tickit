import pytest

from tickit.devices.eiger.eiger import EigerDevice
from tickit.devices.eiger.eiger_status import State


@pytest.fixture
def eiger() -> EigerDevice:
    return EigerDevice()


def test_eiger_constructor():
    EigerDevice()


@pytest.mark.asyncio
async def test_eiger_initialize(eiger: EigerDevice):
    await eiger.initialize()

    assert State.IDLE.value == eiger.get_state()["value"]


@pytest.mark.asyncio
async def test_eiger_arm(eiger: EigerDevice):
    await eiger.arm()

    assert State.READY.value == eiger.get_state()["value"]


@pytest.mark.asyncio
async def test_eiger_disarm(eiger: EigerDevice):
    await eiger.disarm()

    assert State.IDLE.value == eiger.get_state()["value"]


@pytest.mark.asyncio
async def test_eiger_trigger_ints_and_ready(eiger: EigerDevice):
    eiger._set_state(State.READY)
    eiger.settings.trigger_mode = "ints"

    message = await eiger.trigger()

    assert State.ACQUIRE.value == eiger.get_state()["value"]
    assert "Aquiring Data from Eiger..." == message


@pytest.mark.asyncio
async def test_eiger_trigger_not_ints_and_ready(eiger: EigerDevice):
    eiger._set_state(State.READY)

    message = await eiger.trigger()

    assert State.READY.value == eiger.get_state()["value"]
    assert (
        f"Ignoring trigger, state={eiger.status.state},"
        f"trigger_mode={eiger.settings.trigger_mode}" == message
    )


@pytest.mark.asyncio
async def test_eiger_trigger_not_ints_and_not_ready(eiger: EigerDevice):
    eiger._set_state(State.IDLE)

    message = await eiger.trigger()

    assert State.READY.value != eiger.get_state()["value"]
    assert (
        f"Ignoring trigger, state={eiger.status.state},"
        f"trigger_mode={eiger.settings.trigger_mode}" == message
    )


@pytest.mark.asyncio
async def test_eiger_cancel(eiger: EigerDevice):
    await eiger.cancel()

    assert State.READY.value == eiger.get_state()["value"]


@pytest.mark.asyncio
async def test_eiger_abort(eiger: EigerDevice):
    await eiger.abort()

    assert State.IDLE.value == eiger.get_state()["value"]


def test_eiger_get_state(eiger: EigerDevice):
    assert State.NA.value == eiger.get_state()["value"]


def test_eiger_set_state(eiger: EigerDevice):
    eiger._set_state(State.IDLE)

    assert State.IDLE.value == eiger.get_state()["value"]
