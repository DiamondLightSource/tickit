from dataclasses import dataclass

from apischema import deserializer, serializer


@dataclass(frozen=True)
class ByteFormat:
    """An immutable dataclass for custom (de)serialization byte format strings."""

    format: bytes

    @serializer
    def serialize(self) -> str:
        """An apischema serialiazation method which returns a utf-8 decoded string.

        Returns:
            str: A utf-8 decoded string of the format.
        """
        return self.format.decode("utf-8")

    @deserializer
    @staticmethod
    def deserialize(data: str) -> "ByteFormat":
        """An apischema deserialization method builds from a utf-8 encoded string.

        Returns:
            ByteFormat: The deserialized ByteFormat.
        """
        return ByteFormat(data.encode("utf-8"))
