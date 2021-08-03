from dataclasses import dataclass
from typing import Mapping, NewType, Optional

DeviceID = NewType("DeviceID", str)
IoId = NewType("IoId", str)
State = NewType("State", Mapping[str, object])
Changes = NewType("Changes", Mapping[str, object])
SimTime = NewType("SimTime", int)


@dataclass
class Port:
    device: DeviceID
    key: IoId

    def __hash__(self) -> int:
        return (self.device, self.key).__hash__()


@dataclass
class Input:
    target: DeviceID
    time: SimTime
    changes: Changes


@dataclass
class Output:
    source: DeviceID
    time: Optional[SimTime]
    changes: Changes
    call_in: Optional[SimTime]


@dataclass
class Wakeup:
    device: DeviceID
    when: SimTime

    def __lt__(self, value: "Wakeup") -> bool:
        assert isinstance(value, Wakeup)
        return self.when < value.when
