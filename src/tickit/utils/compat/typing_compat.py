import sys

import pydantic

if pydantic.__version__ > 2:
    from pydantic.v1 import BaseModel
    from pydantic.v1.dataclasses import dataclass as pydantic_dataclass
else:
    from pydantic import BaseModel
    from pydantic.dataclasses import dataclass as pydantic_dataclass

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
]
