from dataclasses import dataclass, field
from typing import List

from tickit.devices.eiger.eiger_schema import AccessMode, ro_int, ro_str


@dataclass
class StreamStatus:
    """Eiger stream status taken from the API spec."""

    state: str = field(default="ready", metadata=ro_str())
    error: List[str] = field(
        default_factory=lambda: [],
        metadata=dict(
            value=[], value_type=AccessMode.LIST_STR, access_mode=AccessMode.READ_ONLY
        ),
    )
    dropped: int = field(default=0, metadata=ro_int())
