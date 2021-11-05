import pytest

from tickit.utils.byte_format import ByteFormat


@pytest.fixture
def byte_format() -> ByteFormat:
    return ByteFormat(b"%b/r/n")


def test_byte_format_constructor(byte_format: ByteFormat):
    pass


def test_byteformat_serializer(byte_format: ByteFormat):
    serialized = byte_format.serialize()
    assert "%b/r/n" == serialized


def test_byteformat_deserializer(byte_format: ByteFormat):
    deserialized = byte_format.deserialize("%b/r/n")
    assert ByteFormat(b"%b/r/n") == deserialized
