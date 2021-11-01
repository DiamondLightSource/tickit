import pytest

from tickit.utils.byte_format import ByteFormat


@pytest.fixture
def byteformat() -> ByteFormat:
    return ByteFormat(b"%b/r/n")


def test_byte_format_constructor():
    ByteFormat(b"%b/r/n")


def test_byteformat_serializer():
    byteformat = ByteFormat(b"%b/r/n")
    serialized = byteformat.serialize()

    assert "%b/r/n" == serialized


def test_byteformat_deserializer(byteformat):
    deserialized = byteformat.deserialize("%b/r/n")

    assert ByteFormat(b"%b/r/n") == deserialized
