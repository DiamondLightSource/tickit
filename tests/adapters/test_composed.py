import asyncio

import pytest
from mock import Mock, PropertyMock, create_autospec

from tickit.adapters.composed import ComposedAdapter
from tickit.adapters.interpreters.regex_command import RegexInterpreter
from tickit.adapters.servers.tcp import TcpServer
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
    type(mock_server_config).__kwargs__ = PropertyMock(
        return_value={"host": "localhost", "port": 25566, "format": b"%b\r\n"}
    )
    return mock_server_config


@pytest.fixture
def MockInterpreter() -> Mock:
    return create_autospec(RegexInterpreter, instance=False)


@pytest.fixture
def mock_interpreter() -> Mock:
    return create_autospec(RegexInterpreter, instance=True)


@pytest.fixture
def handle_interrupt():
    async def handle_interrupt():
        return False

    return Mock(handle_interrupt)


@pytest.fixture
def composed_adapter(
    mock_interpreter: Mock,
    mock_device: Mock,
    handle_interrupt: Mock,
    populated_mock_server_config: Mock,
):
    return type(
        "TestComposedAdapter", (ComposedAdapter,), {"_interpreter": mock_interpreter}
    )(mock_device, handle_interrupt, populated_mock_server_config)


def test_composed_adapter_creates_server_with_config_kwargs(
    mock_interpreter: Mock,
    mock_device: Mock,
    handle_interrupt: Mock,
    populated_mock_server_config: Mock,
):
    type(
        "TestComposedAdapter", (ComposedAdapter,), {"_interpreter": mock_interpreter},
    )(mock_device, handle_interrupt, populated_mock_server_config)
    populated_mock_server_config.configures().assert_called_once_with(
        **populated_mock_server_config.__kwargs__
    )


def test_composed_adapter_raises_no_interpreter(
    mock_device: Mock, handle_interrupt: Mock, populated_mock_server_config: Mock,
):
    with pytest.raises(AttributeError):
        type("TestComposedAdapter", (ComposedAdapter,), dict())(
            mock_device, handle_interrupt, populated_mock_server_config
        )


def test_composed_adapter_raises_not_interpreter(
    mock_device: Mock, handle_interrupt: Mock, populated_mock_server_config: Mock,
):
    with pytest.raises(AssertionError):
        type(
            "TestComposedAdapter",
            (ComposedAdapter,),
            {"_interpreter": type("NotInterpreter", tuple(), dict())},
        )(mock_device, handle_interrupt, populated_mock_server_config)


def test_composed_adapter_raises_not_server(
    mock_interpreter: Mock,
    mock_device: Mock,
    handle_interrupt: Mock,
    mock_server_config: Mock,
):
    mock_server_config.configures.return_value = type("NotServer", tuple(), dict())
    type(mock_server_config).__kwargs__ = PropertyMock(return_value=dict())
    with pytest.raises(AssertionError):
        type(
            "TestComposedAdapter",
            (ComposedAdapter,),
            {"_interpreter": mock_interpreter},
        )(mock_device, handle_interrupt, mock_server_config)


def test_composed_adapter_on_connect_does_not_iterate(composed_adapter: Mock):
    with pytest.raises(StopAsyncIteration):
        asyncio.run(composed_adapter.on_connect().__anext__())


def test_composed_adapter_run_forever_runs_server(composed_adapter: Mock):
    asyncio.run(composed_adapter.run_forever())
    composed_adapter._server.run_forever.assert_called_once_with(
        composed_adapter.on_connect, composed_adapter.handle_message
    )


def test_composed_adapter_handle_calls_interpreter_handle(composed_adapter: Mock):
    composed_adapter._interpreter.handle.return_value = ("ReplyMessage", False)
    asyncio.run(composed_adapter.handle_message("TestMessage"))
    composed_adapter._interpreter.handle.assert_called_once_with(
        composed_adapter, "TestMessage"
    )


def test_composed_adapter_handle_does_not_interrupt_for_non_interrupting(
    composed_adapter: Mock,
):
    composed_adapter._interpreter.handle.return_value = ("ReplyMessage", False)
    asyncio.run(composed_adapter.handle_message("TestMessage"))
    composed_adapter.handle_interrupt.assert_not_called()


def test_composed_adapter_handle_interrupts_for_interrupting(composed_adapter: Mock):
    composed_adapter._interpreter.handle.return_value = ("ReplyMessage", True)
    asyncio.run(composed_adapter.handle_message("TestMessage"))
    composed_adapter.handle_interrupt.assert_called_once_with()


def test_composed_adapter_handle_returns_reply(composed_adapter: Mock):
    composed_adapter._interpreter.handle.return_value = ("ReplyMessage", False)
    assert "ReplyMessage" == asyncio.run(composed_adapter.handle_message("TestMessage"))
