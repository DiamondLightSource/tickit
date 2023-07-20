from typing import List

import yaml
from pydantic.v1 import parse_obj_as

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
    return parse_obj_as(List[ComponentConfig], yaml_struct)
