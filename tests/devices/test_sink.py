import logging
from typing import Iterable

import pytest
from mock import Mock, patch

from tickit.core.typedefs import SimTime
from tickit.devices.sink import SinkDevice


@pytest.fixture
def sink() -> SinkDevice:
    return SinkDevice()


@pytest.fixture
def mock_logging() -> Iterable[Mock]:
    with patch("tickit.devices.sink.LOGGER", autospec=True) as mock:
        yield mock


def test_sink_update_method(sink: SinkDevice, caplog):
    inputs = SinkDevice.Inputs({"input": "blah"})
    with caplog.at_level(logging.DEBUG):
        device_update = sink.update(SimTime(0), inputs)
    assert device_update.outputs == {}
    assert device_update.call_at is None

    assert len(caplog.records) == 1
    record: logging.LogRecord = caplog.records[0]

    assert record.levelname == "DEBUG"
    assert record.message == f"Sunk {inputs}"
