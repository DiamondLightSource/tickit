from asyncio import StreamReader, StreamWriter
from typing import AsyncIterable, Awaitable, Callable, Optional

import pytest
from mock import ANY, MagicMock, Mock, patch
from mock.mock import AsyncMock, create_autospec

from tickit.adapters.servers.tcp import TcpServer


@pytest.fixture
def tcp_server() -> TcpServer:
    return TcpServer()


@pytest.fixture
def on_connect() -> Callable[[], AsyncIterable[bytes]]:
    async def on_connect():
        yield b"hello"

    return on_connect


@pytest.fixture
def handler() -> Callable[[bytes], Awaitable[AsyncIterable[bytes]]]:
    async def _handler(message: bytes) -> AsyncIterable[bytes]:
        async def async_iterable() -> AsyncIterable[bytes]:
            yield b"hello"
            yield b""
            yield b"blue"
            yield b"world"
            yield b""

        return async_iterable()

    return _handler


@pytest.fixture
def patch_start_server():
    with patch("asyncio.start_server") as mock:
        yield mock


@pytest.fixture
def mock_stream_reader() -> Mock:
    mock: MagicMock = create_autospec(StreamReader, instance=True)
    mock.read = AsyncMock(side_effect=(b"hello", b"world", b""))
    return mock


@pytest.fixture
def mock_stream_writer() -> Mock:
    mock: MagicMock = create_autospec(StreamWriter, instance=True)
    mock.is_closing = Mock(side_effect=[False, False, True])
    mock.write = Mock()
    mock.drain = AsyncMock()
    return mock


@pytest.mark.asyncio
async def test_TcpServer_run_forever_method(
    tcp_server: TcpServer,
    on_connect: Callable[[], AsyncIterable[bytes]],
    handler: Callable[[bytes], Awaitable[AsyncIterable[Optional[bytes]]]],
    patch_start_server: Mock,
):
    mock_start_server = patch_start_server
    mock_start_server.return_value = AsyncMock()

    await tcp_server.run_forever(on_connect, handler)

    mock_start_server.assert_awaited_once_with(ANY, tcp_server.host, tcp_server.port)
    mock_start_server.return_value.serve_forever.assert_awaited_once()


@pytest.mark.asyncio
async def test_TcpServer_generate_handle_function_method(
    tcp_server: TcpServer,
    on_connect: Callable[[], AsyncIterable[bytes]],
    handler: Callable[[bytes], Awaitable[AsyncIterable[Optional[bytes]]]],
    mock_stream_reader: Mock,
    mock_stream_writer: Mock,
):
    handle_function = tcp_server._generate_handle_function(on_connect, handler)

    assert handle_function is not None

    await handle_function(mock_stream_reader, mock_stream_writer)
