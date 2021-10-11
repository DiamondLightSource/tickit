from enum import Enum
from functools import partial
from typing import Any, Mapping


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


#
# API Access Mode Identifiers
#
class AccessModes(Enum):
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
    field_config, value_type=AccessModes.FLOAT, access_mode=AccessModes.READ_WRITE
)
ro_float: partial = partial(
    field_config, value_type=AccessModes.FLOAT, access_mode=AccessModes.READ_ONLY
)
rw_int: partial = partial(
    field_config, value_type=AccessModes.INT, access_mode=AccessModes.READ_WRITE
)
ro_int: partial = partial(
    field_config, value_type=AccessModes.INT, access_mode=AccessModes.READ_ONLY
)
rw_uint: partial = partial(
    field_config, value_type=AccessModes.UINT, access_mode=AccessModes.READ_WRITE
)
rw_str: partial = partial(
    field_config, value_type=AccessModes.STRING, access_mode=AccessModes.READ_WRITE
)
ro_str: partial = partial(
    field_config, value_type=AccessModes.STRING, access_mode=AccessModes.READ_ONLY
)
rw_bool: partial = partial(
    field_config, value_type=AccessModes.BOOL, access_mode=AccessModes.READ_WRITE
)
rw_float_grid: partial = partial(
    field_config,
    value_type=AccessModes.FLOAT_GRID,
    access_mode=AccessModes.READ_WRITE,
)
rw_uint_grid: partial = partial(
    field_config,
    value_type=AccessModes.UINT_GRID,
    access_mode=AccessModes.READ_WRITE,
)
ro_date: partial = partial(
    field_config, value_type=AccessModes.DATE, access_mode=AccessModes.READ_ONLY
)
