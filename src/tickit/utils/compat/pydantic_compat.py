try:
    from pydantic.v1 import (
        BaseConfig,
        BaseModel,
        Field,
        ValidationError,
        create_model,
        parse_obj_as,
        root_validator,
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
        root_validator,
    )
    from pydantic.dataclasses import dataclass as pydantic_dataclass  # type: ignore
    from pydantic.error_wrappers import ErrorWrapper  # type: ignore

__all__ = [
    "pydantic_dataclass",
    "ErrorWrapper",
    "BaseConfig",
    "BaseModel",
    "create_model",
    "Field",
    "parse_obj_as",
    "ValidationError",
    "root_validator",
]
