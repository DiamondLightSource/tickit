from dataclasses import dataclass, field, fields
from typing import Any, List

from tickit.devices.eiger.eiger_schema import AccessMode


@dataclass
class MonitorStatus:
    """Eiger monitor status taken from the API spec."""

    error: List[str] = field(
        default_factory=lambda: [],
        metadata=dict(
            value=[], value_type=AccessMode.LIST_STR, access_mode=AccessMode.READ_ONLY
        ),
    )

    def __getitem__(self, key: str) -> Any:  # noqa: D105
        f = {}
        for field_ in fields(self):
            f[field_.name] = {
                "value": vars(self)[field_.name],
                "metadata": field_.metadata,
            }
        return f[key]
