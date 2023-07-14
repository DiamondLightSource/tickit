from dataclasses import dataclass


@dataclass(frozen=True)
class ByteFormat:
    """An immutable dataclass for custom (de)serialization byte format strings."""

    format: bytes
