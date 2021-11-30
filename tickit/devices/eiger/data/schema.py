import json
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional, Union

from zmq import Frame

Json = Dict[str, Any]
Sendable = Union[bytes, Frame, memoryview]
MultipartMessage = Iterable[Sendable]


@dataclass
class HeadedBlob:
    """Blob object for frame header."""

    header: Json
    blob: bytes

    def to_message(self) -> MultipartMessage:  # noqa: D102
        yield json.dumps(self.header).encode("utf_8")
        yield self.blob


@dataclass
class ImageBlob(HeadedBlob):
    """Blob object for frame data."""

    dimensions: Json
    times: Json

    def to_message(self) -> MultipartMessage:  # noqa: D102
        yield json.dumps(self.header).encode("utf_8")
        yield json.dumps(self.dimensions).encode("utf_8")
        yield self.blob
        yield json.dumps(self.times).encode("utf_8")


@dataclass
class Header:
    """Class for header json."""

    global_header: Json
    global_header_config: Json

    flat_field: Optional[HeadedBlob] = None
    pixel_mask: Optional[HeadedBlob] = None
    countrate: Optional[HeadedBlob] = None

    def to_message(self) -> MultipartMessage:  # noqa: D102
        yield json.dumps(self.global_header).encode("utf_8")
        yield json.dumps(self.global_header_config).encode("utf_8")

        details = [self.flat_field, self.pixel_mask, self.countrate]
        for detail in details:
            if detail:
                yield from detail.to_message()
