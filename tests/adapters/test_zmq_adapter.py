import asyncio

import aiozmq
import pytest
from mock import Mock, create_autospec

from tickit.adapters.zmqadapter import ZeroMQAdapter
from tickit.core.device import Device


@pytest.fixture
def mock_device() -> Mock:
    device = create_autospec(Device, instance=True)
    device.get_value = Mock()
    device.get_value.return_value = 0
    return device


@pytest.fixture
def raise_interrupt():
    async def raise_interrupt():
        return False

    return Mock(raise_interrupt)


@pytest.fixture
def zeromq_adapter(mock_device) -> ZeroMQAdapter:
    return ZeroMQAdapter(mock_device, raise_interrupt)


def test_zeromq_adapter_constructor(mock_device):
    ZeroMQAdapter(mock_device, raise_interrupt)


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
async def test_zeromq_adapter_close_strean(zeromq_adapter):
    await zeromq_adapter.start_stream()

    await zeromq_adapter.close_stream()
    await asyncio.sleep(0.1)

    assert None is zeromq_adapter._router._transport
    assert None is zeromq_adapter._dealer._transport


@pytest.mark.asyncio
async def test_zeromq_adapter_run_forever(zeromq_adapter):
    await zeromq_adapter.run_forever()

    assert isinstance(zeromq_adapter._router, aiozmq.stream.ZmqStream)
    assert isinstance(zeromq_adapter._dealer, aiozmq.stream.ZmqStream)

    await zeromq_adapter.close_stream()


@pytest.mark.asyncio
async def test_zeromq_adapter_after_update(zeromq_adapter):

    zeromq_adapter.after_update()


# TODO: How to test the message was sent as nothing is returned from send_message()?
@pytest.mark.asyncio
async def test_zeromq_adapter_send_message(zeromq_adapter):
    await zeromq_adapter.start_stream()

    await zeromq_adapter.send_message(0)
