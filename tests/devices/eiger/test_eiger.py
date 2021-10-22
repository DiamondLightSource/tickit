import json

import aiohttp
import pytest
from aiohttp import web
from mock import MagicMock, Mock
from mock.mock import create_autospec

from tickit.devices.eiger.eiger import EigerAdapter, EigerDevice
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
    # Should be 'exts' by default but set just in case
    eiger.settings.trigger_mode = "exts"

    message = await eiger.trigger()

    assert State.READY.value == eiger.get_state()["value"]
    assert (
        f"Ignoring trigger, state={eiger.status.state},"
        f"trigger_mode={eiger.settings.trigger_mode}" == message
    )


@pytest.mark.asyncio
async def test_eiger_trigger_not_ints_and_not_ready(eiger: EigerDevice):

    eiger._set_state(State.IDLE)
    # Should be 'exts' by default but set just in case
    eiger.settings.trigger_mode = "exts"

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


# TODO: Tests for update() once implemented


# # # # # EigerAdapter Tests # # # # #


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
def eiger_adapter(mock_eiger: MagicMock) -> EigerAdapter:
    return EigerAdapter(mock_eiger, raise_interrupt)


def test_eiger_adapter_contructor():
    EigerAdapter(mock_eiger, raise_interrupt)


@pytest.fixture()
def mock_request():
    mock_request = MagicMock(web.Request)
    return mock_request


# # mock_request.match_info = {"parameter_name": mock_get_params["param_name"]}
# @pytest.mark.parametrize(
#     "mock_get_params",
#     [
#         pytest.param(
#             {
#                 "param_name": "count_time",
#                 "return": {
#                     "value": 0.1,
#                     "metadata": {
#                         "value_type": Mock(value="int"),
#                         "access_mode": Mock(value="rw"),
#                     },
#                 },
#                 "expected": {
#                     "value": 0.1,
#                     "value_type": "int",
#                     "access_mode": "rw",
#                     "allowed_values": None,
#                     "max": None,
#                     "min": None,
#                     "unit": None,
#                 },
#             },
#             id="good_request",
#         ),
#         pytest.param(
#             {
#                 "param_name": "wrong_param",
#                 "return": "None",
#                 "expected": {
#                     "value": "None",
#                     "value_type": "string",
#                     "access_mode": "None",
#                     "allowed_values": None,
#                     "max": None,
#                     "min": None,
#                     "unit": None,
#                 },
#             },
#             id="bad_request",
#         ),
#     ],
# )
# @pytest.mark.asyncio
# async def test_eiger_get_config(
#     eiger_adapter: EigerAdapter,
#     mock_request: MagicMock,
#     mock_get_params,
# ):

#     mock_request.match_info = {"parameter_name": mock_get_params["param_name"]}

#     eiger_adapter.device.settings.__getitem__.return_value = mock_get_params["return"]

#     resp = await eiger_adapter.get_config(mock_request)

#     assert mock_get_params["expected"] == json.loads(resp.text)


# @pytest.mark.parametrize(
#     "put_config_test",
#     [
#         pytest.param(
#             {
#                 "state": {"value": "na"},
#                 "param": "count_time",
#                 "expected": '{"sequence_id": 7}',
#             },
#             id="good_put_wrongdevice_state",
#         ),
#         pytest.param(
#             {
#                 "state": {"value": "idle"},
#                 "param": "count_time",
#                 "expected": '{"sequence_id": 8}',
#             },
#             id="good_put_rightdevice_state",
#         ),
#         pytest.param(
#             {
#                 "state": {"value": "idle"},
#                 "param": "wrong_param",
#                 "expected": '{"sequence_id": 9}',
#             },
#             id="bad_put_rightdevice_state",
#         ),
#         pytest.param(
#             {
#                 "state": {"value": "na"},
#                 "param": "wrong_param",
#                 "expected": '{"sequence_id": 7}',
#             },
#             id="bad_put_wrongdevice_state",
#         ),
#     ],
# )
# @pytest.mark.asyncio
# async def test_eiger_put_config(
#     eiger_adapter: EigerAdapter, mock_request: MagicMock, put_config_test
# ):

#     mock_request.match_info = {"parameter_name": put_config_test["param"]}
#     mock_request.json.return_value = {"value": 0.5}

#     eiger_adapter.device.get_state.return_value = put_config_test["state"]

#     resp = await eiger_adapter.put_config(mock_request)

#     assert isinstance(resp, web.Response)
#     assert put_config_test["expected"] == resp.text


# @pytest.mark.parametrize(
#     "get_status_test",
#     [
#         pytest.param(
#             {
#                 "param": "state",
#                 "expected": "State.NA",
#             },
#             id="good_get_status",
#         ),
#         pytest.param(
#             {
#                 "param": "wrong_param",
#                 "expected": "None",
#             },
#             id="bad_get_status",
#         ),
#     ],
# )
# @pytest.mark.asyncio
# async def test_eiger_get_status(
#     eiger_adapter: EigerAdapter, mock_request: MagicMock, get_status_test
# ):

#     mock_request.match_info = {"status_param": get_status_test["param"]}

#     eiger_adapter.device.status.__getitem__.return_value = get_status_test["expected"]

#     resp = await eiger_adapter.get_status(mock_request)

#     assert isinstance(resp, web.Response)
#     assert get_status_test["expected"] == json.loads(str(resp.text))["value"]


# @pytest.mark.parametrize(
#     "command_test",
#     [
#         pytest.param(
#             {"command_method": "initialize_eiger", "expected": '{"sequence_id": 1}'},
#             id="initialize",
#         ),
#         pytest.param(
#             {"command_method": "arm_eiger", "expected": '{"sequence_id": 2}'},
#             id="arm",
#         ),
#         pytest.param(
#             {"command_method": "disarm_eiger", "expected": '{"sequence_id": 3}'},
#             id="arm",
#         ),
#         # TODO: Write proper trigger_eiger() test
#         # pytest.param(
#         #     {"command_method": "trigger_eiger", "expected": str},
#         #     id="trigger",
#         # ),
#         pytest.param(
#             {"command_method": "cancel_eiger", "expected": '{"sequence_id": 5}'},
#             id="cancel",
#         ),
#         pytest.param(
#             {"command_method": "abort_eiger", "expected": '{"sequence_id": 6}'},
#             id="abort",
#         ),
#     ],
# )
# @pytest.mark.asyncio
# async def test_eiger_command(
#     eiger_adapter: EigerAdapter, mock_request: MagicMock, command_test
# ):

#     # eiger_adapter.device.initialize.return_value = State.IDLE

#     command_func = getattr(eiger_adapter, command_test["command_method"])

#     resp = await command_func(mock_request)

#     assert isinstance(resp, web.Response)
#     assert command_test["expected"] == resp.text


# @pytest.mark.asyncio
# async def test_eiger_trigger_command(
#     eiger_adapter: EigerAdapter, mock_request: MagicMock
# ):

#     resp = await eiger_adapter.trigger_eiger(mock_request)

#     assert isinstance(resp, web.Response)
#     # TODO: Add specific strings to this test
#     assert isinstance(resp.text, str)


@pytest.mark.asyncio
@pytest.mark.parametrize("tickit_task", ["examples/configs/eiger.yaml"], indirect=True)
async def test_eiger_system(tickit_task):

    commands = {
        "initialize": {"sequence_id": 1},
        "arm": {"sequence_id": 2},
        "disarm": {"sequence_id": 3},
        "cancel": {"sequence_id": 5},
        "abort": {"sequence_id": 6},
    }  # "trigger"]

    url = "http://0.0.0.0:8081/detector/api/1.8.0/"
    headers = {"content-type": "application/json"}

    async def get_state(expected):
        async with session.get(url + "status/state") as resp:
            assert expected == json.loads(str(await resp.text()))["value"]

    async with aiohttp.ClientSession() as session:
        await get_state(expected="na")

        for key, value in commands.items():
            async with session.put(url + f"command/{key}") as resp:
                assert value == json.loads(str(await resp.text()))

        await get_state(expected="idle")

        async with session.get(url + "config/element") as resp:
            assert json.loads(str(await resp.text()))["value"] == "Co"

        data = '{"value": "Li"}'
        async with session.put(
            url + "config/element", headers=headers, data=data
        ) as resp:
            assert json.loads(str(await resp.text())) == {"sequence_id": 8}

        async with session.get(url + "config/photon_energy") as resp:
            assert json.loads(str(await resp.text()))["value"] == 54.3
