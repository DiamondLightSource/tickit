from asyncio import StreamReader, StreamWriter
from typing import AsyncIterable, Awaitable, Callable, Optional

import pytest
from mock import ANY, MagicMock, Mock, patch
from mock.mock import AsyncMock, create_autospec

from tickit.adapters.io import TcpIo
from tickit.adapters.tcp import CommandAdapter
from tickit.core.adapter import RaiseInterrupt
from tickit.utils.byte_format import ByteFormat


@pytest.fixture
def tcp_io() -> TcpIo:
    return TcpIo(host="localhost", port=25565)


# adapter methods
@pytest.fixture
def handler() -> Callable[[bytes, RaiseInterrupt], Awaitable[AsyncIterable[bytes]]]:
    async def _handler(
        message: bytes,
        raise_interrupt: RaiseInterrupt,
    ) -> AsyncIterable[bytes]:
        async def async_iterable() -> AsyncIterable[bytes]:
            yield b"hello"
            yield b""
            yield b"blue"
            yield b"world"
            yield b""

        return async_iterable()

    return _handler


@pytest.fixture
def on_connect() -> Callable[[], AsyncIterable[bytes]]:
    async def on_connect():
        yield b"hello"

    return on_connect


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


@pytest.fixture
def mock_adapter(handler, on_connect) -> CommandAdapter:
    mock: MagicMock = create_autospec(CommandAdapter, instance=True)
    mock.handle_message = handler
    mock.on_connect = on_connect
    mock.byte_format = ByteFormat(b"%b")
    return mock


@pytest.mark.asyncio
async def test_tcpio_generate_handle_function_method(
    tcp_io: TcpIo,
    on_connect: Callable[[], AsyncIterable[bytes]],
    handler: Callable[
        [bytes, RaiseInterrupt], Awaitable[AsyncIterable[Optional[bytes]]]
    ],
    mock_stream_reader: Mock,
    mock_stream_writer: Mock,
    raise_interrupt: RaiseInterrupt = Mock(),
    byte_format=ByteFormat(b"%b"),
):
    handle_function = tcp_io._generate_handle_function(
        on_connect,
        handler,
        raise_interrupt,
        byte_format,
    )

    assert handle_function is not None

    await handle_function(mock_stream_reader, mock_stream_writer)


@pytest.mark.asyncio
async def test_tcpio_setup_method(
    tcp_io: TcpIo,
    patch_start_server: Mock,
    mock_adapter: CommandAdapter,
    raise_interrupt: RaiseInterrupt = Mock(),
):
    mock_start_server = patch_start_server
    mock_start_server.return_value = AsyncMock()

    await tcp_io.setup(mock_adapter, raise_interrupt)

    mock_start_server.assert_awaited_once_with(ANY, tcp_io.host, tcp_io.port)
