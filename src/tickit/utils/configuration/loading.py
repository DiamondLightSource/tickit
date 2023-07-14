from importlib import import_module
from typing import List
from pydantic.v1 import parse_obj_as

import yaml

from tickit.core.components.component import ComponentConfig


def read_configs(config_path) -> List[ComponentConfig]:
    """A utility function which reads and deserializes configs.

    A utility function which reads config files, performs yaml deserialization,
    loads the required internal and external modules then subsequently performs
    apischema deserialization to produce a list of component configuration objects.

    Args:
        config_path ([type]): The path to the config file.

    Returns:
        List[Component]: A list of component configuration objects.
    """
    with open(config_path, "r") as config_file:
        yaml_struct = yaml.load(config_file, Loader=yaml.Loader)
    configs = [deserialize(yaml_obj) for yaml_obj in yaml_struct]
    return configs


def deserialize(d):
    fullname = d["type"]
    pkg, clsname = fullname.rsplit(".", maxsplit=1)
    cls = getattr(import_module(pkg), clsname)
    return parse_obj_as(cls, d)
