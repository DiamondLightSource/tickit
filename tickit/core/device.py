from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Type

from tickit.core.adapter import AdapterConfig
from tickit.core.typedefs import DeviceID, IoId, SimTime, State
from tickit.utils.compat.typing_compat import Protocol, runtime_checkable
from tickit.utils.configuration.configurable import configurable, configurable_base


@dataclass
class UpdateEvent:
    state: State
    call_in: Optional[SimTime]


@runtime_checkable
class Device(Protocol):
    def update(self, time: SimTime, inputs: State) -> UpdateEvent:
        pass


@configurable_base
@dataclass
class DeviceConfig:
    name: DeviceID
    adapters: List[AdapterConfig]
    inputs: Dict[IoId, Tuple[DeviceID, IoId]]

    @staticmethod
    def configures() -> Type[Device]:
        raise NotImplementedError

    @property
    def __kwargs__(self):
        raise NotImplementedError


class ConfigurableDevice:
    def __init_subclass__(cls) -> None:
        cls = configurable(DeviceConfig)(cls)
