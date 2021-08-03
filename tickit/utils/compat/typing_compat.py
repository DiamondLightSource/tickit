import sys

if sys.version_info >= (3, 8):
    from typing import Protocol, TypedDict, runtime_checkable  # pragma: no cover
else:
    from typing_extensions import (  # pragma: no cover
        Protocol,
        TypedDict,
        runtime_checkable,
    )

__all__ = ["Protocol", "TypedDict", "runtime_checkable"]
