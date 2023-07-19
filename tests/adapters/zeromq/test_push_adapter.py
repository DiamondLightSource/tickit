import asyncio
from typing import Sequence

import aiozmq
import pytest
import pytest_asyncio
from mock import MagicMock, Mock
from mock.mock import AsyncMock, create_autospec

from tickit.adapters.zeromq.push_adapter import (
    SocketFactory,
    ZeroMqMessage,
    ZeroMqPushAdapter,
)
from tickit.core.adapter import RaiseInterrupt
from tickit.core.device import Device
from tickit.utils.compat.pydantic_compat import BaseModel

_HOST = "test.host"
_PORT = 12345


@pytest.fixture
def mock_device() -> Device:
    return create_autospec(Device)


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
def zeromq_adapter(mock_socket_factory: aiozmq.ZmqStream) -> ZeroMqPushAdapter:
    return ZeroMqPushAdapter(
        host=_HOST,
        port=_PORT,
        socket_factory=mock_socket_factory,
    )


@pytest_asyncio.fixture
async def running_zeromq_adapter(
    zeromq_adapter: ZeroMqPushAdapter,
    socket_created: asyncio.Event,
    mock_device: Device,
    mock_raise_interrupt: RaiseInterrupt,
) -> ZeroMqPushAdapter:
    asyncio.create_task(zeromq_adapter.run_forever(mock_device, mock_raise_interrupt))
    await asyncio.wait_for(socket_created.wait(), timeout=2.0)
    return zeromq_adapter


@pytest.mark.asyncio
async def test_socket_not_created_until_run_forever(
    zeromq_adapter: ZeroMqPushAdapter,
    mock_socket_factory: AsyncMock,
    socket_created: asyncio.Event,
    mock_device: Device,
    mock_raise_interrupt: RaiseInterrupt,
) -> None:
    mock_socket_factory.assert_not_called()
    asyncio.create_task(zeromq_adapter.run_forever(mock_device, mock_raise_interrupt))
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


@pytest.mark.asyncio
@pytest.mark.parametrize("message,serialized_message", MESSGAGES)
async def test_serializes_and_sends_message(
    running_zeromq_adapter: ZeroMqPushAdapter,
    mock_socket: MagicMock,
    message: ZeroMqMessage,
    serialized_message: Sequence[bytes],
) -> None:
    await running_zeromq_adapter.send_message(message)
    mock_socket.write.assert_called_once_with(serialized_message)


@pytest.mark.asyncio
async def test_socket_cleaned_up_on_cancel(
    mock_device: Device,
    mock_raise_interrupt: RaiseInterrupt,
) -> None:
    adapter_a = ZeroMqPushAdapter()
    adapter_b = ZeroMqPushAdapter()
    for adapter in (adapter_a, adapter_b):
        task = asyncio.create_task(
            adapter.run_forever(
                mock_device,
                mock_raise_interrupt,
            )
        )
        await adapter.send_message([b"test"])
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        assert task.done()
