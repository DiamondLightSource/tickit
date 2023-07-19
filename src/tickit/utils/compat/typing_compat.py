import sys

try:
    from pydantic.v1 import (
        BaseConfig,
        BaseModel,
        Field,
        ValidationError,
        create_model,
        parse_obj_as,
    )
    from pydantic.v1.dataclasses import dataclass as pydantic_dataclass
    from pydantic.v1.error_wrappers import ErrorWrapper
except ImportError:
    from pydantic import (  # type: ignore
        BaseConfig,
        BaseModel,
        Field,
        ValidationError,
        create_model,
        parse_obj_as,
    )
    from pydantic.dataclasses import dataclass as pydantic_dataclass  # type: ignore
    from pydantic.error_wrappers import ErrorWrapper  # type: ignore


if sys.version_info >= (3, 8):
    from typing import Protocol, TypedDict, runtime_checkable
elif sys.version_info >= (3, 5):
    from typing_extensions import Protocol, TypedDict, runtime_checkable

__all__ = [
    "Protocol",
    "TypedDict",
    "runtime_checkable",
    "pydantic_dataclass",
    "ErrorWrapper",
    "BaseConfig",
    "BaseModel",
    "create_model",
    "Field",
    "parse_obj_as",
    "ValidationError",
]
