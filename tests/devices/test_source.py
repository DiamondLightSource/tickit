from typing import Iterable

import pytest
from mock import Mock, patch

from tickit.core.typedefs import SimTime
from tickit.devices.source import Source


@pytest.fixture
def source() -> Source:
    return Source(value=42)


@pytest.fixture
def mock_logging() -> Iterable[Mock]:
    with patch("tickit.devices.source.logger", autospec=True) as mock:
        yield mock


def test_source_constructor_method(source: Source):
    assert source.value == 42


def test_source_update_method(source: Source):
    device_update = source.update(SimTime(0), inputs={})
    assert device_update.outputs["value"] == 42
    assert device_update.call_at is None
