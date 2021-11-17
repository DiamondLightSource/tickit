import pytest

from tickit.devices.eiger.stream.stream_config import StreamConfig

# # # # # Eiger StreamConfig Tests # # # # #


@pytest.fixture
def stream_config() -> StreamConfig:
    return StreamConfig()


def test_eiger_stream_config_constructor():
    StreamConfig()


def test_eiger_stream_config_getitem(stream_config):
    assert "enabled" == stream_config["mode"]["value"]
