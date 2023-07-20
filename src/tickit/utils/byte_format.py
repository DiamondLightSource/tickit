from pydantic.v1 import BaseModel, validator


class ByteFormat(BaseModel):
    """An immutable dataclass for custom (de)serialization byte format strings."""

    class Config:
        json_encoders = {bytes: lambda b: b.decode("utf-8")}

    format: bytes

    def __init__(self, format: bytes):
        super().__init__(format=format)

    @validator("format")
    def encode_string(cls, v):
        if isinstance(v, str):
            v = v.encode("utf-8")
        return v
