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

READ_ONLY = "r"
WRITE_ONLY = "w"
READ_WRITE = "rw"
FLOAT = "float"
INT = "int"
UINT = "uint"
STRING = "string"
LIST_STR = "string[]"
BOOL = "bool"
FLOAT_GRID = "float[][]"
UINT_GRID = "uint[][]"
DATE = "date"
NONE = "none"

#
# Shortcuts to creating dataclass field metadata
#

rw_float = partial(field_config, value_type=FLOAT, access_mode=READ_WRITE)
ro_float = partial(field_config, value_type=FLOAT, access_mode=READ_ONLY)
rw_int = partial(field_config, value_type=INT, access_mode=READ_WRITE)
ro_int = partial(field_config, value_type=INT, access_mode=READ_ONLY)
rw_uint = partial(field_config, value_type=UINT, access_mode=READ_WRITE)
rw_str = partial(field_config, value_type=STRING, access_mode=READ_WRITE)
ro_str = partial(field_config, value_type=STRING, access_mode=READ_ONLY)
rw_bool = partial(field_config, value_type=BOOL, access_mode=READ_WRITE)
rw_float_grid = partial(field_config, value_type=FLOAT_GRID, access_mode=READ_WRITE)
rw_uint_grid = partial(field_config, value_type=UINT_GRID, access_mode=READ_WRITE)
ro_date = partial(field_config, value_type=DATE, access_mode=READ_ONLY)
