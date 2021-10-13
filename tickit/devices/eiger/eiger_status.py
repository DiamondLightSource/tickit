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
    errors: List[str] = field(default_factory=lambda: [])
    temp: float = field(default=24.5)
    humidity: float = field(default=0.2)
    time: datetime = field(default=datetime.now())

    # TODO: Why does this not work when returning a generic TypeVar????
    def __getitem__(self, key: str) -> Any:
        """[Summary]."""
        f = {}
        for field_ in fields(self):
            f[field_.name] = vars(self)[field_.name]
        return f[key]
