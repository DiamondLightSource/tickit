import json

import aiohttp
import pytest
from aiohttp import web
from mock import MagicMock, Mock
from mock.mock import create_autospec

from tickit.devices.eiger.eiger import EigerDevice, EigerRESTAdapter
from tickit.devices.eiger.eiger_settings import EigerSettings
from tickit.devices.eiger.eiger_status import EigerStatus, State

# # # # # EigerDevice Tests # # # # #


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


# # # # # EigerRESTAdapter Tests # # # # #


@pytest.fixture
def mock_status() -> MagicMock:
    status = create_autospec(EigerStatus, instance=True)
    status.state = State.NA
    return status


@pytest.fixture
def mock_settings() -> MagicMock:
    settings = create_autospec(EigerSettings, instance=True)
    settings.count_time = {
        "value": 0.1,
        "metadata": {"value_type": Mock(value="int"), "access_mode": Mock(value="rw")},
    }
    return settings


@pytest.fixture
def mock_eiger(mock_status: MagicMock, mock_settings: MagicMock) -> MagicMock:
    mock_eiger = create_autospec(EigerDevice, instance=True)
    mock_eiger.status = mock_status
    mock_eiger.settings = mock_settings
    return mock_eiger


@pytest.fixture
def raise_interrupt():
    async def raise_interrupt():
        return False

    return Mock(raise_interrupt)


@pytest.fixture
def eiger_adapter(mock_eiger: MagicMock) -> EigerRESTAdapter:
    return EigerRESTAdapter(mock_eiger, raise_interrupt)


def test_eiger_adapter_contructor():
    EigerRESTAdapter(mock_eiger, raise_interrupt)


@pytest.fixture()
def mock_request():
    mock_request = MagicMock(web.Request)
    return mock_request


@pytest.mark.asyncio
@pytest.mark.parametrize("tickit_task", ["examples/configs/eiger.yaml"], indirect=True)
async def test_eiger_system(tickit_task):

    commands = {
        "initialize": {"sequence_id": 1},
        "disarm": {"sequence_id": 3},
        "cancel": {"sequence_id": 5},
        "abort": {"sequence_id": 6},
    }

    url = "http://0.0.0.0:8081/detector/api/1.8.0/"
    headers = {"content-type": "application/json"}

    filewriter_url = "http://0.0.0.0:8081/filewriter/api/1.8.0/"
    monitor_url = "http://0.0.0.0:8081/monitor/api/1.8.0/"
    stream_url = "http://0.0.0.0:8081/stream/api/1.8.0/"

    async def get_status(status, expected):
        async with session.get(url + f"status/{status}") as resp:
            assert expected == json.loads(str(await resp.text()))["value"]

    async with aiohttp.ClientSession() as session:
        await get_status(status="state", expected="na")

        # Test setting config var before Eiger set up
        data = '{"value": "test"}'
        async with session.put(
            url + "config/element", headers=headers, data=data
        ) as resp:
            assert json.loads(str(await resp.text())) == {"sequence_id": 7}

        # Test each command
        for key, value in commands.items():
            async with session.put(url + f"command/{key}") as resp:
                assert value == json.loads(str(await resp.text()))

        await get_status(status="doesnt_exist", expected="None")

        await get_status(status="board_000/th0_temp", expected=24.5)

        await get_status(status="board_000/doesnt_exist", expected="None")

        await get_status(status="builder/dcu_buffer_free", expected=0.5)

        await get_status(status="builder/doesnt_exist", expected="None")

        # Test Eiger in IDLE state
        await get_status(status="state", expected="idle")

        async with session.get(url + "config/doesnt_exist") as resp:
            assert json.loads(str(await resp.text()))["value"] == "None"

        data = '{"value": "test"}'
        async with session.put(
            url + "config/doesnt_exist", headers=headers, data=data
        ) as resp:
            assert json.loads(str(await resp.text())) == {"sequence_id": 9}

        async with session.get(url + "config/element") as resp:
            assert json.loads(str(await resp.text()))["value"] == "Co"

        data = '{"value": "Li"}'
        async with session.put(
            url + "config/element", headers=headers, data=data
        ) as resp:
            assert json.loads(str(await resp.text())) == {"sequence_id": 8}

        async with session.get(url + "config/photon_energy") as resp:
            assert json.loads(str(await resp.text()))["value"] == 54.3

        async with session.get(filewriter_url + "config/mode") as resp:
            assert "enabled" == json.loads(str(await resp.text()))["value"]

        async with session.get(filewriter_url + "status/state") as resp:
            assert "ready" == json.loads(str(await resp.text()))["value"]

        async with session.get(monitor_url + "config/mode") as resp:
            assert "enabled" == json.loads(str(await resp.text()))["value"]

        async with session.get(monitor_url + "status/error") as resp:
            assert [] == json.loads(str(await resp.text()))["value"]

        async with session.get(stream_url + "config/mode") as resp:
            assert "enabled" == json.loads(str(await resp.text()))["value"]

        async with session.get(stream_url + "status/state") as resp:
            assert "ready" == json.loads(str(await resp.text()))["value"]

        async with session.put(url + "command/arm") as resp:
            assert {"sequence_id": 2} == json.loads(str(await resp.text()))

        async with session.put(url + "command/trigger") as resp:
            assert {"sequence_id": 4} == json.loads(str(await resp.text()))
