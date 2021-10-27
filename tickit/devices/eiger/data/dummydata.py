from typing import List

from tickit.devices.eiger.data.image import Image, deduce_encoding

_DUMMY_IMAGE_BLOBS: List[bytes] = []


def dummy_image(index: int) -> Image:
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


def dummy_image_blob() -> bytes:
    """Returns the current dummy data blob.

    Return the raw bytes of a compressed image
    taken from the stream of a real Eiger detector.

    Returns:
        A compressed image as a bytes object.
    """
    if _DUMMY_IMAGE_BLOBS:
        return _DUMMY_IMAGE_BLOBS[0]
    else:
        with open("tickit/devices/eiger/resources/frame_sample", "rb") as f:
            _DUMMY_IMAGE_BLOBS.append(f.read())
        return dummy_image_blob()
