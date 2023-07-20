import pytest

from tickit.utils.byte_format import ByteFormat


@pytest.fixture
def byte_format() -> ByteFormat:
    return ByteFormat(b"%b/r/n")


def test_byteformat_serializer(byte_format: ByteFormat):
    d = byte_format.json()
    assert '{"format": "%b/r/n"}' == d
    assert '{"format": b"%b/r/n"}' != d


def test_validates_string_to_bytes(byte_format: ByteFormat):
    assert byte_format == ByteFormat("%b/r/n")  # type: ignore
