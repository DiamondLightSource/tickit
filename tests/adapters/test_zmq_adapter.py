import aiozmq
import pytest
from mock import Mock, create_autospec

from tickit.adapters.zmqadapter import ZeroMQAdapter, ZeroMQStream
from tickit.core.device import Device


@pytest.fixture
def MockDevice() -> Mock:
    return create_autospec(Device, instance=False)


@pytest.fixture
def mock_device() -> Mock:
    return create_autospec(Device, instance=True)


@pytest.fixture
def zeromq_stream() -> ZeroMQStream:
    return ZeroMQStream()


def test_zeromq_stream_constructor():
    ZeroMQStream()


@pytest.fixture
def zeromq_adapter() -> ZeroMQAdapter:
    return ZeroMQAdapter(zeromq_stream)


def test_zeromq_adapter_constructor():
    ZeroMQAdapter(zeromq_stream)


@pytest.mark.asyncio
async def test_zeromq_adapter_start_stream(zeromq_adapter):
    await zeromq_adapter.start_stream()

    assert isinstance(zeromq_adapter._router, aiozmq.stream.ZmqStream)
    assert isinstance(zeromq_adapter._dealer, aiozmq.stream.ZmqStream)
