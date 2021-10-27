from dataclasses import dataclass


@dataclass
class Image:
    """Dataclass to create a basic Image object."""

    index: int
    hash: str
    dtype: str
    data: bytes
    encoding: str


def deduce_encoding(compression_type: str, dtype: str) -> str:
    """Function to deduce the encoding string for the image."""
    if compression_type == "lz4":
        return "lz4<"
    elif compression_type == "bslz4":
        if dtype == "uint16":
            return "bs16-lz4<"
    raise KeyError(
        f"Unknown combination, compression={compression_type}, " " dtype={dtype}"
    )
