from importlib import import_module
from typing import Any, Dict, List, Optional, Type

import yaml
from apischema import deserialize
from apischema.conversions import AnyConversion, Conversion
from apischema.conversions.conversions import Conversion
from apischema.conversions.converters import default_serialization

from tickit.core.components.component import ComponentConfig


def config_importing_conversion(typ: Type) -> Optional[AnyConversion]:
    """Create a conversion that imports the module of a ComponentConfig.

    When a ComponentConfig is requested from a dict, take its fully qualified
    name from the tagged union dict and import it before deserializing it
    """
    if typ is ComponentConfig:

        def conversion(d: Dict[str, Any]) -> ComponentConfig:
            # We can't use the deserialization union above as the classes
            # haven't been imported so won't appear in __subclasses__, so use a
            # single element dict instead
            assert len(d) == 1, d
            fullname, args = list(d.items())[0]
            pkg, clsname = fullname.rsplit(".", maxsplit=1)
            cls = getattr(import_module(pkg), clsname)
            return deserialize(cls, args)

        return Conversion(conversion, source=dict, target=ComponentConfig)

    return default_serialization(typ)


def read_configs(config_path) -> List[ComponentConfig]:
    """A utility function which reads and deserializes configs.

    A utility function which reads config files, performs yaml deserialization,
    loads the required internal and external modules then subsequently performs
    apischema deserialization to produce a list of component configuration objects.

    Args:
        config_path ([type]): The path to the config file.

    Returns:
        List[ComponentConfig]: A list of component configuration objects.
    """
    yaml_struct = yaml.load(open(config_path, "r"), Loader=yaml.Loader)
    configs = deserialize(
        List[ComponentConfig],
        yaml_struct,
        default_conversion=config_importing_conversion,
    )
    return configs
