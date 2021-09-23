import re
from contextlib import suppress
from importlib import import_module
from typing import Deque, List

import apischema
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
        List[ComponentConfig]: A list of component configuration objects.
    """
    yaml_struct = yaml.load(open(config_path, "r"), Loader=yaml.Loader)
    load_modules(yaml_struct)
    configs = apischema.deserialize(List[ComponentConfig], yaml_struct)
    return configs


def load_modules(yaml_struct) -> None:
    """A utility function which loads modules referenced within a configuration yaml struct.

    Args:
        yaml_struct ([type]): The possibly nested yaml structure generated when a
            configuration file is loaded.
    """

    def possibly_import_class(path: str) -> None:
        if re.fullmatch(r"[\w+\.]+\.\w+", path):
            with suppress(ModuleNotFoundError):
                import_module(path)

    to_crawl = Deque([yaml_struct])
    while to_crawl:
        cfg = to_crawl.popleft()
        if isinstance(cfg, list):
            to_crawl.extend(cfg)
        elif isinstance(cfg, dict):
            to_crawl.extend(cfg.values())
            for key in cfg.keys():
                possibly_import_class(str(key))
        else:
            possibly_import_class(str(cfg))
