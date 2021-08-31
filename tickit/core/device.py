from dataclasses import dataclass
from typing import Optional, Type

from tickit.core.typedefs import SimTime, State
from tickit.utils.compat.typing_compat import Protocol, runtime_checkable
from tickit.utils.configuration.configurable import configurable, configurable_base


@dataclass(frozen=True)
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
    @staticmethod
    def configures() -> Type[Device]:
        raise NotImplementedError

    @property
    def kwargs(self):
        raise NotImplementedError


class ConfigurableDevice:
    def __init_subclass__(cls) -> None:
        cls = configurable(DeviceConfig)(cls)
