from dataclasses import dataclass
from typing import Dict, List, NewType, Optional, Tuple

DeviceID = NewType("DeviceID", str)
IoId = NewType("IoId", str)
State = NewType("State", Dict[IoId, object])
Changes = NewType("Changes", Dict[IoId, object])
SimTime = NewType("SimTime", int)


@dataclass
class AdapterConfig:
    adapter_class: str


@dataclass
class DeviceConfig:
    name: DeviceID
    device_class: str
    adapters: List[AdapterConfig]
    inputs: Dict[IoId, Tuple[DeviceID, IoId]]


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

    def __or__(self, other):
        assert isinstance(other, Input)
        assert self.target == other.target
        assert self.time == other.time
        return Input(self.target, self.time, dict(self.state).__or__(other.state))

    def __ror__(self, other):
        assert isinstance(other, Input)
        assert self.target == other.target
        assert self.time == other.time
        return Input(self.target, self.time, dict(other.state).__ror__(self.state))

    def __ior__(self, other):
        assert isinstance(other, Input)
        assert self.target == other.target
        assert self.time == other.time
        return Input(self.target, self.time, self.state.__ior__(other.state))


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

    def __lt__(self, other):
        assert isinstance(other, Wakeup)
        return self.when < other.when
