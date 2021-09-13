import pytest
from mock import MagicMock, Mock, PropertyMock, create_autospec

from tickit.adapters.composed import ComposedAdapter
from tickit.adapters.servers.tcp import TcpServer
from tickit.core.adapter import Interpreter
from tickit.devices.toy.remote_controlled import RemoteControlled


@pytest.fixture
def MockDevice() -> Mock:
    return create_autospec(RemoteControlled, instance=False)


@pytest.fixture
def mock_device() -> Mock:
    return create_autospec(RemoteControlled, instance=True)


@pytest.fixture
def MockServer() -> Mock:
    return create_autospec(TcpServer, instance=False)


@pytest.fixture
def mock_server() -> Mock:
    return create_autospec(TcpServer, instance=True)


@pytest.fixture
def MockServerConfig() -> Mock:
    return create_autospec(TcpServer.Config, instance=False)


@pytest.fixture
def mock_server_config() -> Mock:
    return create_autospec(TcpServer.Config, instance=True)


@pytest.fixture
def populated_mock_server_config(mock_server_config: Mock, MockServer: Mock) -> Mock:
    mock_server_config.configures.return_value = MockServer
    type(mock_server_config).kwargs = PropertyMock(
        return_value={"host": "localhost", "port": 25566, "format": b"%b\r\n"}
    )
    return mock_server_config


@pytest.fixture
def MockInterpreter() -> Mock:
    return MagicMock(Interpreter, instance=False)


@pytest.fixture
def mock_interpreter() -> Mock:
    return MagicMock(Interpreter, instance=True)


@pytest.fixture
def raise_interrupt():
    async def raise_interrupt():
        return False

    return Mock(raise_interrupt)


@pytest.fixture
def composed_adapter(
    mock_device: Mock, raise_interrupt: Mock, mock_server: Mock, mock_interpreter: Mock,
):
    return type("TestComposedAdapter", (ComposedAdapter,), {})(
        mock_device, raise_interrupt, mock_server, mock_interpreter
    )


@pytest.mark.asyncio
async def test_composed_adapter_on_connect_does_not_iterate(composed_adapter: Mock):
    with pytest.raises(StopAsyncIteration):
        await composed_adapter.on_connect().__anext__()


@pytest.mark.asyncio
async def test_composed_adapter_run_forever_runs_server(composed_adapter: Mock):
    await composed_adapter.run_forever()
    composed_adapter._server.run_forever.assert_called_once_with(
        composed_adapter.on_connect, composed_adapter.handle_message
    )


@pytest.mark.asyncio
async def test_composed_adapter_handle_calls_interpreter_handle(composed_adapter: Mock):
    composed_adapter._interpreter.handle.return_value = ("ReplyMessage", False)
    await composed_adapter.handle_message("TestMessage")
    composed_adapter._interpreter.handle.assert_called_once_with(
        composed_adapter, "TestMessage"
    )


@pytest.mark.asyncio
async def test_composed_adapter_handle_does_not_interrupt_for_non_interrupting(
    composed_adapter: Mock,
):
    composed_adapter._interpreter.handle.return_value = ("ReplyMessage", False)
    await composed_adapter.handle_message("TestMessage")
    composed_adapter._raise_interrupt.assert_not_called()


@pytest.mark.asyncio
async def test_composed_adapter_raise_interrupts_for_interrupting(
    composed_adapter: Mock,
):
    composed_adapter._interpreter.handle.return_value = ("ReplyMessage", True)
    await composed_adapter.handle_message("TestMessage")
    composed_adapter._raise_interrupt.assert_called_once_with()


@pytest.mark.asyncio
async def test_composed_adapter_handle_returns_reply(composed_adapter: Mock):
    composed_adapter._interpreter.handle.return_value = ("ReplyMessage", False)
    assert "ReplyMessage" == await composed_adapter.handle_message("TestMessage")
