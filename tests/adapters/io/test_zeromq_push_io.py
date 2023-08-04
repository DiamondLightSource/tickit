import asyncio
from typing import AsyncGenerator, Sequence

import aiozmq
import pytest
import pytest_asyncio
from mock import AsyncMock, MagicMock, Mock
from pydantic.v1 import BaseModel

from tickit.adapters.io.zeromq_push_io import SocketFactory, ZeroMqMessage, ZeroMqPushIo
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


@pytest_asyncio.fixture
async def io(mock_socket_factory: AsyncMock) -> AsyncGenerator[ZeroMqPushIo, None]:
    io = ZeroMqPushIo(
        host=_HOST,
        port=_PORT,
        socket_factory=mock_socket_factory,
    )
    yield io
    await io.shutdown()


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


class SimpleMessage(BaseModel):
    foo: int
    bar: str


class SubMessage(BaseModel):
    baz: bool


class NestedMessage(BaseModel):
    foo: int
    bar: SubMessage


MESSGAGES = [
    ([b"foo"], [b"foo"]),
    (["foo"], [b'"foo"']),
    ([b"foo", b"bar"], [b"foo", b"bar"]),
    ([b"foo", "bar"], [b"foo", b'"bar"']),
    ([{"foo": 1, "bar": "baz"}], [b'{"foo": 1, "bar": "baz"}']),
    ([{"foo": 1, "bar": {"baz": False}}], [b'{"foo": 1, "bar": {"baz": false}}']),
    ([SimpleMessage(foo=1, bar="baz")], [b'{"foo": 1, "bar": "baz"}']),
    (
        [NestedMessage(foo=1, bar=SubMessage(baz=False))],
        [b'{"foo": 1, "bar": {"baz": false}}'],
    ),
]


@pytest_asyncio.fixture
async def running_zeromq_adapter(
    zeromq_adapter_container: AdapterContainer,
    socket_created: asyncio.Event,
    mock_raise_interrupt: RaiseInterrupt,
) -> AdapterContainer:
    asyncio.create_task(zeromq_adapter_container.run_forever(mock_raise_interrupt))
    await asyncio.wait_for(socket_created.wait(), timeout=2.0)
    return zeromq_adapter_container


@pytest.mark.asyncio
@pytest.mark.parametrize("message,serialized_message", MESSGAGES)
async def test_serializes_and_sends_message(
    running_zeromq_adapter: AdapterContainer,
    mock_socket: MagicMock,
    message: ZeroMqMessage,
    serialized_message: Sequence[bytes],
) -> None:
    assert isinstance(running_zeromq_adapter.io, ZeroMqPushIo)
    await running_zeromq_adapter.io.send_message(message)
    mock_socket.write.assert_called_once_with(serialized_message)


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
        assert isinstance(container.io, ZeroMqPushIo)
        await container.io.send_message([b"test"])
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        assert task.done()
