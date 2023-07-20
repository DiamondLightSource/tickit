import pydantic.v1.dataclasses
from pydantic.v1 import validator


@pydantic.v1.dataclasses.dataclass
class ByteFormat:
    """An immutable dataclass for custom (de)serialization byte format strings."""

    format: bytes

    def __str__(self):
        return str({"format": self.format.decode("utf-8")})

    @validator("format")
    def encode_string(cls, v):
        if isinstance(v, str):
            v = v.encode("utf-8")
        return v
