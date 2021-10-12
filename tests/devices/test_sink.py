from typing import Iterable

import pytest
from mock import Mock, patch

from tickit.core.typedefs import SimTime
from tickit.devices.sink import Sink


@pytest.fixture
def sink() -> Sink:
    return Sink()


@pytest.fixture
def mock_logging() -> Iterable[Mock]:
    with patch("tickit.devices.sink.LOGGER", autospec=True) as mock:
        yield mock


def test_sink_update_method(sink: Sink, mock_logging: Mock):
    device_update = sink.update(SimTime(0), {"input": "blah"})
    assert device_update.outputs == {}
    assert device_update.call_at is None
    assert mock_logging.debug.called
