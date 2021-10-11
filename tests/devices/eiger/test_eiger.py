import pytest
from aiohttp import web
from mock import MagicMock, Mock
from mock.mock import create_autospec

from tickit.devices.eiger.eiger import Eiger, EigerAdapter
from tickit.devices.eiger.eiger_settings import EigerSettings
from tickit.devices.eiger.eiger_status import EigerStatus, State

# # # # # Eiger Tests # # # # #


@pytest.fixture
def eiger() -> Eiger:
    return Eiger()


def test_eiger_constructor():
    Eiger()


@pytest.mark.asyncio
async def test_eiger_initialize(eiger: Eiger):
    await eiger.initialize()

    assert State.IDLE == eiger.get_state()


@pytest.mark.asyncio
async def test_eiger_arm(eiger: Eiger):
    await eiger.arm()

    assert State.READY == eiger.get_state()


@pytest.mark.asyncio
async def test_eiger_disarm(eiger: Eiger):
    await eiger.disarm()

    assert State.IDLE == eiger.get_state()


@pytest.mark.asyncio
async def test_eiger_trigger_ints_and_ready(eiger: Eiger):

    eiger._set_state(State.READY)
    eiger.settings.trigger_mode = "ints"

    message = await eiger.trigger()

    assert State.ACQUIRE == eiger.get_state()
    assert "Aquiring Data from Eiger..." == message


@pytest.mark.asyncio
async def test_eiger_trigger_not_ints_and_ready(eiger: Eiger):

    eiger._set_state(State.READY)
    # Should be 'exts' by default but set just in case
    eiger.settings.trigger_mode = "exts"

    message = await eiger.trigger()

    assert State.READY == eiger.get_state()
    assert (
        f"Ignoring trigger, state={eiger.status.state},"
        f"trigger_mode={eiger.settings.trigger_mode}" == message
    )


@pytest.mark.asyncio
async def test_eiger_trigger_not_ints_and_not_ready(eiger: Eiger):

    eiger._set_state(State.IDLE)
    # Should be 'exts' by default but set just in case
    eiger.settings.trigger_mode = "exts"

    message = await eiger.trigger()

    assert State.READY != eiger.get_state()
    assert (
        f"Ignoring trigger, state={eiger.status.state},"
        f"trigger_mode={eiger.settings.trigger_mode}" == message
    )


@pytest.mark.asyncio
async def test_eiger_cancel(eiger: Eiger):
    await eiger.cancel()

    assert State.READY == eiger.get_state()


@pytest.mark.asyncio
async def test_eiger_abort(eiger: Eiger):
    await eiger.abort()

    assert State.IDLE == eiger.get_state()


def test_eiger_get_state(eiger: Eiger):
    assert State.NA == eiger.get_state()


def test_eiger_set_state(eiger: Eiger):

    eiger._set_state(State.IDLE)

    assert State.IDLE == eiger.get_state()


# TODO: Tests for update() once implemented


# # # # # EigerAdapter Tests # # # # #


@pytest.fixture
def mock_status() -> MagicMock:
    return create_autospec(EigerStatus, instance=True)


@pytest.fixture
def mock_settings() -> MagicMock:
    return create_autospec(EigerSettings, instance=True)


@pytest.fixture
def mock_eiger(mock_status: MagicMock, mock_settings: MagicMock) -> MagicMock:
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
def eiger_adapter(mock_eiger: MagicMock) -> EigerAdapter:
    return EigerAdapter(mock_eiger, raise_interrupt, host="localhost", port=8081)


def test_eiger_adapter_contructor():
    EigerAdapter(mock_eiger, raise_interrupt, host="localhost", port=8081)


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
    mock_request.json.return_value = {"value": 0.5}

    return mock_request


@pytest.fixture
def mock_good_get_status_request():
    mock_request = MagicMock(web.Request)
    mock_request.match_info = {"status_param": "state"}

    return mock_request


@pytest.fixture
def mock_bad_get_status_request():
    mock_request = MagicMock(web.Request)
    mock_request.match_info = {"status_param": "wrong_param"}

    return mock_request


@pytest.mark.asyncio
async def test_eiger_get_config(
    eiger_adapter: EigerAdapter, mock_good_get_request: MagicMock
):

    resp = await eiger_adapter.get_config(mock_good_get_request)

    assert isinstance(resp, web.Response)


@pytest.mark.asyncio
async def test_eiger_good_get_config(
    eiger_adapter: EigerAdapter, mock_good_get_request: MagicMock
):

    resp = await eiger_adapter.get_config(mock_good_get_request)

    assert "None" != resp.text


@pytest.mark.asyncio
async def test_eiger_bad_get_config(
    eiger_adapter: EigerAdapter, mock_bad_get_request: MagicMock
):

    resp = await eiger_adapter.get_config(mock_bad_get_request)

    assert "None" == resp.text


@pytest.mark.asyncio
async def test_eiger_good_put_config_wrong_device_state(
    eiger_adapter: EigerAdapter, mock_good_put_request: MagicMock
):

    eiger_adapter._device.get_state.return_value = State.NA

    resp = await eiger_adapter.put_config(mock_good_put_request)

    assert isinstance(resp, web.Response)
    assert "Eiger not initialized or is currently running." == resp.text


@pytest.mark.asyncio
async def test_eiger_good_put_config_right_device_state(
    eiger_adapter: EigerAdapter, mock_good_put_request: MagicMock
):

    eiger_adapter._device.get_state.return_value = State.IDLE

    resp = await eiger_adapter.put_config(mock_good_put_request)

    assert isinstance(resp, web.Response)
    assert "Set: count_time to 0.5" == resp.text


@pytest.mark.asyncio
async def test_eiger_bad_put_config_right_device_state(
    eiger_adapter: EigerAdapter, mock_bad_put_request: MagicMock
):

    eiger_adapter._device.get_state.return_value = State.IDLE

    resp = await eiger_adapter.put_config(mock_bad_put_request)

    assert isinstance(resp, web.Response)
    assert "Eiger has no config variable: wrong_param" == resp.text


@pytest.mark.asyncio
async def test_eiger_bad_put_config_wrong_device_state(
    eiger_adapter: EigerAdapter, mock_bad_put_request: MagicMock
):

    eiger_adapter._device.get_state.return_value = State.NA

    resp = await eiger_adapter.put_config(mock_bad_put_request)

    assert isinstance(resp, web.Response)
    assert "Eiger not initialized or is currently running." == resp.text


@pytest.mark.asyncio
async def test_eiger_good_get_status(
    eiger_adapter: EigerAdapter, mock_good_get_status_request: MagicMock
):

    eiger_adapter._device.status.state = State.NA

    resp = await eiger_adapter.get_status(mock_good_get_status_request)

    assert isinstance(resp, web.Response)
    assert "State.NA" == resp.text


@pytest.mark.asyncio
async def test_eiger_bad_get_status(
    eiger_adapter: EigerAdapter, mock_bad_get_status_request: MagicMock
):

    eiger_adapter._device.status.state = State.NA

    resp = await eiger_adapter.get_status(mock_bad_get_status_request)

    assert isinstance(resp, web.Response)
    assert "None" == resp.text


@pytest.mark.asyncio
async def test_eiger_initialize_command(
    eiger_adapter: EigerAdapter, mock_good_put_request: MagicMock
):

    eiger_adapter._device._set_state
    eiger_adapter._device.initialize.return_value = State.IDLE

    resp = await eiger_adapter.initialize_eiger(mock_good_put_request)

    assert isinstance(resp, web.Response)
    assert "Initializing Eiger..." == resp.text


@pytest.mark.asyncio
async def test_eiger_arm_command(
    eiger_adapter: EigerAdapter, mock_good_put_request: MagicMock
):

    resp = await eiger_adapter.arm_eiger(mock_good_put_request)

    assert isinstance(resp, web.Response)
    assert "Arming Eiger..." == resp.text


@pytest.mark.asyncio
async def test_eiger_disarm_command(
    eiger_adapter: EigerAdapter, mock_good_put_request: MagicMock
):

    resp = await eiger_adapter.disarm_eiger(mock_good_put_request)

    assert isinstance(resp, web.Response)
    assert "Disarming Eiger..." == resp.text


@pytest.mark.asyncio
async def test_eiger_trigger_command(
    eiger_adapter: EigerAdapter, mock_good_put_request: MagicMock
):

    resp = await eiger_adapter.trigger_eiger(mock_good_put_request)

    assert isinstance(resp, web.Response)
    # TODO: Add specific strings to this test
    assert isinstance(resp.text, str)


@pytest.mark.asyncio
async def test_eiger_cancel_command(
    eiger_adapter: EigerAdapter, mock_good_put_request: MagicMock
):

    resp = await eiger_adapter.cancel_eiger(mock_good_put_request)

    assert isinstance(resp, web.Response)
    assert "Cancelling Eiger..." == resp.text


@pytest.mark.asyncio
async def test_eiger_abort_command(
    eiger_adapter: EigerAdapter, mock_good_put_request: MagicMock
):

    resp = await eiger_adapter.abort_eiger(mock_good_put_request)

    assert isinstance(resp, web.Response)
    assert "Aborting Eiger..." == resp.text
