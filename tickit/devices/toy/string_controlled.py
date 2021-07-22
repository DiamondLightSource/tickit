from dataclasses import dataclass
from typing import Awaitable, Callable

from tickit.adapters.composed import ComposedAdapter, ComposedAdapterConfig
from tickit.adapters.interpreters.string_regex import StringRegexInterpreter
from tickit.core.device import Device, DeviceConfig, UpdateEvent
from tickit.core.typedefs import IoId, SimTime, State


@dataclass
class StringControlledConfig(DeviceConfig):
    device_class = "tickit.devices.toy.string_controlled.StringControlled"
    initial_observed: int = 0
    initual_unobserved: int = 42


class StringControlled:
    def __init__(self, config: StringControlledConfig) -> None:
        self.observed = config.initial_observed
        self.unobserved = config.initual_unobserved

    def update(self, time: SimTime, inputs: State) -> UpdateEvent:
        return UpdateEvent(State({IoId("observed"): self.observed}), None)


@dataclass
class StringControlledAdapterConfig(ComposedAdapterConfig):
    adapter_class = "tickit.devices.toy.string_controlled.StringControlledAdapter"


class StringControlledAdapter(ComposedAdapter):
    _interpreter = StringRegexInterpreter()

    def __init__(
        self,
        device: Device,
        handle_interrupt: Callable[[], Awaitable[None]],
        config: StringControlledAdapterConfig,
    ) -> None:
        super().__init__(device, handle_interrupt, config)

    @_interpreter.command(r"O")
    def get_observed(self) -> str:
        return str(self._device.observed)

    @_interpreter.command(r"O=(\d+\.?\d*)", interrupt=True)
    def set_observed(self, value: int) -> str:
        self._device.observed = value
        return "Observed set to {}".format(self._device.observed)

    @_interpreter.command(r"U")
    def get_unobserved(self) -> str:
        return str(self._device.unobserved)

    @_interpreter.command(r"U=(\d+\.?\d*)")
    def set_unobserved(self, value: int) -> str:
        self._device.unobserved = value
        return "Unobserved set to {}".format(self._device.unobserved)
