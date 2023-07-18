import sys

try:
    import pydantic.v1 as pydantic
except ImportError:
    import pydantic  # type: ignore[no-redef]


if sys.version_info >= (3, 8):
    from typing import Protocol, TypedDict, runtime_checkable
elif sys.version_info >= (3, 5):
    from typing_extensions import Protocol, TypedDict, runtime_checkable

__all__ = ["Protocol", "TypedDict", "runtime_checkable", "pydantic"]
