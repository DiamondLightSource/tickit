import pytest

from tickit.devices.eiger.stream.stream_status import StreamStatus

# # # # # Eiger StreamStatus Tests # # # # #


@pytest.fixture
def stream_status() -> StreamStatus:
    return StreamStatus()


def test_eiger_stream_status_constructor():
    StreamStatus()


def test_eiger_status_getitem(stream_status):
    assert "ready" == stream_status["state"]["value"]
