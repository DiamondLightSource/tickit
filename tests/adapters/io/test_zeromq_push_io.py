import asyncio

import aiozmq
import pytest
from mock import AsyncMock, MagicMock, Mock

from tickit.adapters.io.zeromq_push_io import SocketFactory, ZeroMqPushIo
from tickit.adapters.zmq import ZeroMqPushAdapter
from tickit.core.adapter import AdapterContainer, RaiseInterrupt

_HOST = "127.0.0.1"
_PORT = 5530


@pytest.fixture
def mock_raise_interrupt() -> RaiseInterrupt:
    async def raise_interrupt():
        return False

    return Mock(raise_interrupt)


@pytest.fixture
def mock_socket() -> aiozmq.ZmqStream:
    return MagicMock(aiozmq.ZmqStream)


@pytest.fixture
def socket_created() -> asyncio.Event:
    return asyncio.Event()


@pytest.fixture
def mock_socket_factory(
    mock_socket: aiozmq.ZmqStream, socket_created: asyncio.Event
) -> SocketFactory:
    def make_socket(host: str, port: int) -> aiozmq.ZmqStream:
        socket_created.set()
        return mock_socket

    factory = AsyncMock()
    factory.side_effect = make_socket
    return factory


@pytest.fixture
def io(mock_socket_factory: AsyncMock) -> ZeroMqPushIo:
    return ZeroMqPushIo(
        host=_HOST,
        port=_PORT,
        socket_factory=mock_socket_factory,
    )


@pytest.fixture
def adapter() -> ZeroMqPushAdapter:
    return ZeroMqPushAdapter()


@pytest.fixture
def zeromq_adapter_container(
    adapter: ZeroMqPushAdapter,
    io: ZeroMqPushIo,
) -> AdapterContainer:
    return AdapterContainer(adapter, io)


@pytest.mark.asyncio
async def test_socket_not_created_until_run_forever(
    zeromq_adapter_container: AdapterContainer,
    mock_socket_factory: AsyncMock,
    socket_created: asyncio.Event,
    mock_raise_interrupt: RaiseInterrupt,
) -> None:
    mock_socket_factory.assert_not_called()
    asyncio.create_task(zeromq_adapter_container.run_forever(mock_raise_interrupt))
    await asyncio.wait_for(socket_created.wait(), timeout=2.0)
    mock_socket_factory.assert_called_once_with(_HOST, _PORT)


@pytest.mark.asyncio
async def test_socket_cleaned_up_on_cancel(
    adapter: ZeroMqPushAdapter,
    io: ZeroMqPushIo,
    mock_raise_interrupt: RaiseInterrupt,
) -> None:
    adapter_a = AdapterContainer(adapter, io)
    adapter_b = AdapterContainer(adapter, io)

    for container in (adapter_a, adapter_b):
        task = asyncio.create_task(
            container.run_forever(
                mock_raise_interrupt,
            )
        )
        await container.io.send_message([b"test"])
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        assert task.done()
