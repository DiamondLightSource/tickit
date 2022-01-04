import os
from pathlib import Path

import tickit


def test_all_ticket_folders_are_packages() -> None:
    top_level = Path(tickit.__file__).parent
    _assert_are_packages(top_level)


def _assert_are_packages(top_level: Path) -> None:
    non_packages = []
    for dirpath, _, _ in os.walk(top_level):
        init = Path(dirpath) / "__init__.py"
        if not init.exists():
            non_packages += [dirpath]
    assert (
        not non_packages
    ), f"The following directories need an __init__.py: {non_packages}"
