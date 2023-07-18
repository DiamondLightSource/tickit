import sys

import pydantic

if pydantic.__version__.startswith("1"):
    from pydantic import BaseModel, parse_obj_as
    from pydantic.dataclasses import dataclass as pydantic_dataclass
else:
    from pydantic.v1 import BaseModel, parse_obj_as  # type: ignore
    from pydantic.v1.dataclasses import dataclass as pydantic_dataclass  # type: ignore

if sys.version_info >= (3, 8):
    from typing import Protocol, TypedDict, runtime_checkable
elif sys.version_info >= (3, 5):
    from typing_extensions import Protocol, TypedDict, runtime_checkable

__all__ = [
    "Protocol",
    "TypedDict",
    "runtime_checkable",
    "pydantic_dataclass",
    "BaseModel",
    "parse_obj_as"
]
