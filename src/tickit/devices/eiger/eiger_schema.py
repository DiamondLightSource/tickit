from dataclasses import dataclass, field
from enum import Enum
from functools import partial
from typing import Any, Generic, List, Mapping, Optional, TypeVar

T = TypeVar("T")


def field_config(**kwargs) -> Mapping[str, Any]:
    """Helper function to create a typesafe dictionary.

    Helper function to create a typesafe dictionary to be inserted as
    dataclass metadata.

    Args:
        kwargs: Key/value pairs to go into the metadata

    Returns:
        Mapping[str, Any]: A dictionary of {key: value} where all keys are strings
    """
    return dict(**kwargs)


class AccessMode(Enum):
    """Possible access modes for field metadata."""

    READ_ONLY: str = "r"
    WRITE_ONLY: str = "w"
    READ_WRITE: str = "rw"
    FLOAT: str = "float"
    INT: str = "int"
    UINT: str = "uint"
    STRING: str = "string"
    LIST_STR: str = "string[]"
    BOOL: str = "bool"
    FLOAT_GRID: str = "float[][]"
    UINT_GRID: str = "uint[][]"
    DATE: str = "date"
    NONE: str = "none"


#
# Shortcuts to creating dataclass field metadata
#
rw_float: partial = partial(
    field_config, value_type=AccessMode.FLOAT, access_mode=AccessMode.READ_WRITE
)
ro_float: partial = partial(
    field_config, value_type=AccessMode.FLOAT, access_mode=AccessMode.READ_ONLY
)
rw_int: partial = partial(
    field_config, value_type=AccessMode.INT, access_mode=AccessMode.READ_WRITE
)
ro_int: partial = partial(
    field_config, value_type=AccessMode.INT, access_mode=AccessMode.READ_ONLY
)
rw_uint: partial = partial(
    field_config, value_type=AccessMode.UINT, access_mode=AccessMode.READ_WRITE
)
rw_str: partial = partial(
    field_config, value_type=AccessMode.STRING, access_mode=AccessMode.READ_WRITE
)
ro_str: partial = partial(
    field_config, value_type=AccessMode.STRING, access_mode=AccessMode.READ_ONLY
)
rw_bool: partial = partial(
    field_config, value_type=AccessMode.BOOL, access_mode=AccessMode.READ_WRITE
)
rw_float_grid: partial = partial(
    field_config,
    value_type=AccessMode.FLOAT_GRID,
    access_mode=AccessMode.READ_WRITE,
)
rw_uint_grid: partial = partial(
    field_config,
    value_type=AccessMode.UINT_GRID,
    access_mode=AccessMode.READ_WRITE,
)
ro_date: partial = partial(
    field_config, value_type=AccessMode.DATE, access_mode=AccessMode.READ_ONLY
)


@dataclass
class Value(Generic[T]):
    """Schema for a value to be returned by the API. Most fields are optional."""

    value: T
    value_type: str
    access_mode: Optional[AccessMode] = None
    unit: Optional[str] = None
    min: Optional[T] = None
    max: Optional[T] = None
    allowed_values: Optional[List[str]] = None


@dataclass
class SequenceComplete:
    """Schema for confirmation returned by operations that do not return values."""

    sequence_id: int = field(default=1, metadata=ro_int())
