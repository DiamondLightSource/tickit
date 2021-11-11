from dataclasses import dataclass
from typing import List


@dataclass
class Image:
    """Dataclass to create a basic Image object."""

    index: int
    hash: str
    dtype: str
    data: bytes
    encoding: str

    @classmethod
    def create_dummy_image(cls, index: int) -> "Image":
        """Returns an Image object wrapping the dummy blob using the metadata provided.

        Args:
            index (int): The index of the Image in the current acquisition.

        Returns:
            Image: An Image object wrapping the dummy blob.
        """
        data = dummy_image_blob()
        hsh = str(hash(data))
        dtype = "uint16"
        encoding = deduce_encoding("bslz4", dtype)
        return Image(index, hsh, dtype, data, encoding)


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


_DUMMY_IMAGE_BLOBS: List[bytes] = []


def dummy_image_blob() -> bytes:
    """Returns the current dummy data blob.

    Return the raw bytes of a compressed image
    taken from the stream of a real Eiger detector.

    Returns:
        A compressed image as a bytes object.
    """
    if not _DUMMY_IMAGE_BLOBS:
        with open("tickit/devices/eiger/resources/frame_sample", "rb") as frame_file:
            _DUMMY_IMAGE_BLOBS.append(frame_file.read())
    return _DUMMY_IMAGE_BLOBS[0]
