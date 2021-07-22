from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from tickit.core.adapter import AdapterConfig
from tickit.core.typedefs import DeviceID, IoId, SimTime, State
from tickit.utils.compat.typing_compat import Protocol, runtime_checkable


@dataclass
class UpdateEvent:
    state: State
    call_in: Optional[SimTime]


@dataclass
class DeviceConfig:
    name: DeviceID
    device_class: str
    adapters: List[AdapterConfig]
    inputs: Dict[IoId, Tuple[DeviceID, IoId]]


@runtime_checkable
class Device(Protocol):
    def update(self, time: SimTime, inputs: State) -> UpdateEvent:
        ...
