from dataclasses import dataclass
from typing import Generic, Hashable, Mapping, Optional, Type, TypeVar

from tickit.core.typedefs import SimTime
from tickit.utils.compat.typing_compat import Protocol, runtime_checkable
from tickit.utils.configuration.configurable import configurable, configurable_base

InMap = TypeVar("InMap", bound=Mapping[str, Hashable])
OutMap = TypeVar("OutMap", bound=Mapping[str, Hashable])


@dataclass
class DeviceUpdate(Generic[OutMap]):
    outputs: OutMap
    call_in: Optional[SimTime]


@runtime_checkable
class Device(Protocol[InMap, OutMap]):
    def update(self, time: SimTime, inputs: InMap) -> DeviceUpdate[OutMap]:
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
