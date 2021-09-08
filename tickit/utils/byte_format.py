from dataclasses import dataclass

from apischema import deserializer, serializer


@dataclass(frozen=True)
class ByteFormat:
    format: bytes

    @serializer
    def serialize(self) -> str:
        return self.format.decode("utf-8")

    @deserializer
    @staticmethod
    def deserialize(data: str) -> "ByteFormat":
        return ByteFormat(data.encode("utf-8"))
