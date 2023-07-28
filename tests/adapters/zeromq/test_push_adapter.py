import asyncio
from typing import List, Sequence

import aiozmq
import pytest
import pytest_asyncio
from mock import MagicMock, Mock
from mock.mock import AsyncMock, create_autospec
from pydantic.v1 import BaseModel

from tickit.adapters.interpreters.zeromq_socket.push_interpreter import (
    ZeroMqPushInterpreter,
)
from tickit.adapters.io.zeromq_push_io import ZeroMqMessage, ZeroMqPushIo
from tickit.core.adapter import RaiseInterrupt
from tickit.core.device import Device
import zmq

_HOST = "127.0.0.1"
_PORT = 5530


@pytest.fixture
def mock_device() -> Device:
    return create_autospec(Device)


@pytest.fixture
def mock_raise_interrupt() -> RaiseInterrupt:
    async def raise_interrupt():
        return False

    return Mock(raise_interrupt)


@pytest.fixture
def io() -> ZeroMqPushIo:
    return ZeroMqPushIo(
        host=_HOST,
        port=_PORT,
    )


@pytest.fixture
def adapter() -> ZeroMqPushInterpreter:
    return ZeroMqPushInterpreter()


@pytest_asyncio.fixture
async def client() -> aiozmq.ZmqStream:
    addr = f"tcp://{_HOST}:{_PORT}"
    socket = await aiozmq.create_zmq_stream(zmq.PULL, connect=addr)
    yield socket
    socket.close()
    await socket.drain()
    await asyncio.sleep(0.5)


@pytest_asyncio.fixture
async def running_adapter(
    adapter: ZeroMqPushInterpreter,
    io: ZeroMqPushIo,
    mock_raise_interrupt: RaiseInterrupt,
) -> ZeroMqPushInterpreter:
    await io.setup(adapter, mock_raise_interrupt)
    yield adapter
    await io.shutdown()
    await asyncio.sleep(0.5)


# @pytest.mark.asyncio
# async def test_socket_not_created_until_run_forever(
#     running_adapter: ZeroMqPushInterpreter,
#     io: ZeroMqPushIo,
#     mock_raise_interrupt: RaiseInterrupt,
# ) -> None:
#     mock_socket_factory.assert_not_called()
#     asyncio.create_task(zeromq_adapter.run_forever(mock_device, mock_raise_interrupt))
#     await asyncio.wait_for(socket_created.wait(), timeout=2.0)
#     mock_socket_factory.assert_called_once_with(_HOST, _PORT)


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
    running_adapter: ZeroMqPushInterpreter,
    client: aiozmq.ZmqStream,
    message: ZeroMqMessage,
    serialized_message: Sequence[bytes],
) -> None:
    future = asyncio.Future()

    async def read() -> None:
        reply = await asyncio.wait_for(client.read(), timeout=1.0)
        future.set_result(reply)

    task = asyncio.create_task(read())
    running_adapter.add_message_to_stream(message)
    await task
    assert future.result() == serialized_message


# async def test_socket_cleaned_up_on_cancel(
#     mock_device: Device,
#     mock_raise_interrupt: RaiseInterrupt,
# ) -> None:
#     adapter_a = ZeroMqPushAdapter()
#     adapter_b = ZeroMqPushAdapter()
#     for adapter in (adapter_a, adapter_b):
#         task = asyncio.create_task(
#             adapter.run_forever(
#                 mock_device,
#                 mock_raise_interrupt,
#             )
#         )
#         await adapter.send_message([b"test"])
#         task.cancel()
#         try:
#             await task
#         except asyncio.CancelledError:
#             pass
#         assert task.done()

# @pytest.mark.asyncio
# async def test_socket_cleaned_up_on_cancel(
#     mock_device: Device,
#     mock_raise_interrupt: RaiseInterrupt,
# ) -> None:
#     adapter_a = ZeroMqPushAdapter()
#     adapter_b = ZeroMqPushAdapter()
#     for adapter in (adapter_a, adapter_b):
#         task = asyncio.create_task(
#             adapter.run_forever(
#                 mock_device,
#                 mock_raise_interrupt,
#             )
#         )
#         await adapter.send_message([b"test"])
#         task.cancel()
#         try:
#             await task
#         except asyncio.CancelledError:
#             pass
#         assert task.done()
