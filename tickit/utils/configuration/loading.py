import re
from contextlib import suppress
from importlib import import_module
from typing import Deque, List

import apischema
import yaml

from tickit.core.components.component import ComponentConfig


def read_configs(config_path) -> List[ComponentConfig]:
    yaml_struct = yaml.load(open(config_path, "r"), Loader=yaml.Loader)
    load_modules(yaml_struct)
    configs = apischema.deserialize(List[ComponentConfig], yaml_struct)
    return configs


def load_modules(yaml_struct) -> None:
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
