from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Union


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

    def __getitem__(self, key: str) -> Union[State, List, float, datetime]:
        """[Summary]."""
        PROPERTY_KEYS = asdict(self)
        return PROPERTY_KEYS[key]
