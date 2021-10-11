# import logging
# import struct
# from typing import Optional

import pytest

# import aiohttp
from aiohttp import web
from mock import MagicMock, Mock
from mock.mock import create_autospec

# from tickit.core.device import DeviceUpdate
# from tickit.core.typedefs import SimTime
from tickit.devices.eiger.eiger import Eiger, EigerAdapter
from tickit.devices.eiger.eiger_settings import EigerSettings
from tickit.devices.eiger.eiger_status import EigerStatus, State

# # # # # Eiger Tests # # # # #


@pytest.fixture
def eiger() -> Eiger:
    return Eiger()


def test_eiger_constructor():
    Eiger()


# def test_eiger_initialize():


# TODO: Tests for update() once implemented


# # # # # EigerAdapter Tests # # # # #


@pytest.fixture
def mock_status() -> MagicMock:
    return create_autospec(EigerStatus, instance=True)


@pytest.fixture
def mock_settings() -> MagicMock:
    return create_autospec(EigerSettings, instance=True)


@pytest.fixture
def mock_eiger(mock_status, mock_settings) -> MagicMock:
    mock_eiger = create_autospec(Eiger, instance=True)
    mock_eiger.status = mock_status
    mock_eiger.settings = mock_settings
    return mock_eiger


@pytest.fixture
def raise_interrupt():
    async def raise_interrupt():
        return False

    return Mock(raise_interrupt)


@pytest.fixture
def mock_eiger_adapter(mock_eiger):
    return EigerAdapter(mock_eiger, raise_interrupt, host="localhost", port=8081)


def test_eiger_adapter_contructor():
    EigerAdapter(mock_eiger, raise_interrupt, host="localhost", port=8081)


# @pytest.fixture
# async def mock_client() -> Mock:
#     app = web.Application()
#     client = await aiohttp_client(app)
#     return client


DETECTOR_API = "http://localhost:8081/detector/api/1.8"


@pytest.fixture
def mock_good_get_request():
    mock_request = MagicMock(web.Request)
    mock_request.match_info = {"parameter_name": "count_time"}

    return mock_request


@pytest.fixture
def mock_bad_get_request():
    mock_request = MagicMock(web.Request)
    mock_request.match_info = {"parameter_name": "wrong_param"}

    return mock_request


@pytest.fixture
def mock_good_put_request():
    mock_request = MagicMock(web.Request)
    mock_request.match_info = {"parameter_name": "count_time"}
    mock_request.json.return_value = {"value": 0.5}

    return mock_request


@pytest.fixture
def mock_bad_put_request():
    mock_request = MagicMock(web.Request)
    mock_request.match_info = {"parameter_name": "wrong_param"}
    mock_request.value = 0.5

    return mock_request


# @pytest.mark.asyncio
# async def test_eiger_endpoint_response(mock_eiger_adapter):

#     async with aiohttp.ClientSession() as session:
#         resp = await session.get(f"{DETECTOR_API}" + "/config/count_time")

#         assert isinstance(resp, web.Response)


@pytest.mark.asyncio
async def test_eiger_get_config(mock_eiger_adapter, mock_good_get_request):

    resp = await mock_eiger_adapter.get_config(mock_good_get_request)

    assert isinstance(resp, web.Response)


@pytest.mark.asyncio
async def test_eiger_good_get_config(mock_eiger_adapter, mock_good_get_request):

    resp = await mock_eiger_adapter.get_config(mock_good_get_request)

    assert resp.text != "None"


@pytest.mark.asyncio
async def test_eiger_bad_get_config(mock_eiger_adapter, mock_bad_get_request):

    resp = await mock_eiger_adapter.get_config(mock_bad_get_request)

    assert resp.text == "None"


@pytest.mark.asyncio
async def test_eiger_good_put_config_wrong_device_state(
    mock_eiger_adapter, mock_good_put_request
):

    # Eiger starts off in State.NA, so no state needs to be set

    resp = await mock_eiger_adapter.put_config(mock_good_put_request)

    assert isinstance(resp, web.Response)
    assert resp.text == "Eiger not initialized or is currently running."


@pytest.mark.asyncio
async def test_eiger_good_put_config_right_device_state(
    mock_eiger_adapter, mock_good_put_request
):

    mock_eiger_adapter._device.get_state.return_value = State.IDLE

    resp = await mock_eiger_adapter.put_config(mock_good_put_request)

    assert isinstance(resp, web.Response)
    assert resp.text == "Set: count_time to 0.5"


@pytest.mark.asyncio
async def test_eiger_bad_put_config_right_device_state(
    mock_eiger_adapter, mock_bad_put_request
):

    mock_eiger_adapter._device.get_state.return_value = State.IDLE

    resp = await mock_eiger_adapter.put_config(mock_bad_put_request)

    assert isinstance(resp, web.Response)
    assert resp.text == "Eiger has no config variable: wrong_param"


@pytest.mark.asyncio
async def test_eiger_bad_put_config_wrong_device_state(
    mock_eiger_adapter, mock_bad_put_request
):

    resp = await mock_eiger_adapter.put_config(mock_bad_put_request)

    assert isinstance(resp, web.Response)
    assert resp.text == "Eiger not initialized or is currently running."
