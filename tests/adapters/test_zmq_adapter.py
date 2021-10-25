import asyncio

import aiozmq
import pytest
from mock import Mock

from tickit.adapters.zmqadapter import ZeroMQAdapter


@pytest.fixture
@pytest.mark.asyncio
async def process_message_queue() -> Mock:
    async def _process_message_queue():
        return True

    return Mock(_process_message_queue)


@pytest.fixture
def zeromq_adapter(process_message_queue) -> ZeroMQAdapter:
    zmq_adapter = ZeroMQAdapter()
    zmq_adapter._process_message_queue = process_message_queue
    zmq_adapter._message_queue = Mock(asyncio.Queue)
    return zmq_adapter


def test_zeromq_adapter_constructor():
    ZeroMQAdapter()


# TODO: Would it be better to use something like this?
# @pytest.fixture
# def patch_aiozmq_create_zmq_stream() -> Iterable[Mock]:
#     with patch(
#         "tickit.adapters.zmqadapter.aiozmq.create_zmq_stream", autospec=True
#     ) as mock:
#         yield mock


@pytest.mark.asyncio
async def test_zeromq_adapter_start_stream(zeromq_adapter):
    await zeromq_adapter.start_stream()

    assert isinstance(zeromq_adapter._router, aiozmq.stream.ZmqStream)
    assert isinstance(zeromq_adapter._dealer, aiozmq.stream.ZmqStream)

    await zeromq_adapter.close_stream()


@pytest.mark.asyncio
async def test_zeromq_adapter_close_stream(zeromq_adapter):
    await zeromq_adapter.start_stream()

    await zeromq_adapter.close_stream()
    await asyncio.sleep(0.1)

    assert None is zeromq_adapter._router._transport
    assert None is zeromq_adapter._dealer._transport


# TODO: This currently runs indefinitely due to recent changes, and hangs
# @pytest.mark.asyncio
# async def test_zeromq_adapter_run_forever(zeromq_adapter):

#     await zeromq_adapter.run_forever()

#     assert isinstance(zeromq_adapter._router, aiozmq.stream.ZmqStream)
#     assert isinstance(zeromq_adapter._dealer, aiozmq.stream.ZmqStream)

#     await zeromq_adapter.close_stream()


@pytest.mark.asyncio
async def test_zeromq_adapter_after_update(zeromq_adapter):

    zeromq_adapter.after_update()


# TODO: How to test the message was sent as nothing is returned from send_message()?
@pytest.mark.asyncio
async def test_zeromq_adapter_send_message(zeromq_adapter):
    await zeromq_adapter.start_stream()

    await zeromq_adapter.send_message(0)
