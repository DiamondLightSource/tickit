from dataclasses import dataclass, field, fields
from datetime import datetime
from enum import Enum
from typing import Any, List


class State(Enum):
    """Possible states of the Eiger detector."""

    NA = "na"
    READY = "ready"
    INITIALIZE = "initialize"
    CONFIGURE = "configure"
    ACQUIRE = "acquire"
    IDLE = "idle"
    TEST = "test"
    ERROR = "error"


@dataclass
class EigerStatus:
    """Stores the status parameters of the Eiger detector."""

    state: State = field(default=State.NA)
    errors: List[str] = field(default_factory=list)
    th0_temp: float = field(default=24.5)
    th0_humidity: float = field(default=0.2)
    time: datetime = field(default=datetime.now())
    dcu_buffer_free: float = field(default=0.5)

    def __getitem__(self, key: str) -> Any:  # noqa: D105
        f = {}
        for field_ in fields(self):
            f[field_.name] = vars(self)[field_.name]
        return f[key]
