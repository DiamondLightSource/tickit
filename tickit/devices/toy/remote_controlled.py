import struct
from dataclasses import dataclass
from typing import Awaitable, Callable

from tickit.adapters.composed import ComposedAdapter, ComposedAdapterConfig
from tickit.adapters.interpreters.regex_command import RegexInterpreter
from tickit.core.device import Device, DeviceConfig, UpdateEvent
from tickit.core.typedefs import IoId, SimTime, State


@dataclass
class RemoteControlledConfig(DeviceConfig):
    device_class = "tickit.devices.toy.remote_controlled.RemoteControlled"
    initial_observed: int = 0
    initual_unobserved: int = 42


class RemoteControlled:
    def __init__(self, config: RemoteControlledConfig) -> None:
        self.observed = config.initial_observed
        self.unobserved = config.initual_unobserved

    def update(self, time: SimTime, inputs: State) -> UpdateEvent:
        return UpdateEvent(State({IoId("observed"): self.observed}), None)


@dataclass
class RemoteControlledAdapterConfig(ComposedAdapterConfig):
    adapter_class = "tickit.devices.toy.remote_controlled.RemoteControlledAdapter"


class RemoteControlledAdapter(ComposedAdapter):
    _interpreter = RegexInterpreter()

    def __init__(
        self,
        device: Device,
        handle_interrupt: Callable[[], Awaitable[None]],
        config: RemoteControlledAdapterConfig,
    ) -> None:
        super().__init__(device, handle_interrupt, config)

    @_interpreter.command(b"\x01")
    def get_observed_bytes(self) -> bytes:
        return struct.pack(">i", self._device.observed)

    @_interpreter.command(r"O", format="utf-8")
    def get_observed_str(self) -> str:
        return str(self._device.observed)

    @_interpreter.command(b"\x01(.{4})", interrupt=True)
    def set_observed_bytes(self, value: bytes) -> bytes:
        self._device.observed = struct.unpack(">i", value)[0]
        return struct.pack(">i", self._device.observed)

    @_interpreter.command(r"O=(\d+\.?\d*)", interrupt=True, format="utf-8")
    def set_observed_str(self, value: int) -> str:
        self._device.observed = value
        return "Observed set to {}".format(self._device.observed)

    @_interpreter.command(b"\x02")
    def get_unobserved_bytes(self) -> bytes:
        return struct.pack(">i", self._device.unobserved)

    @_interpreter.command(r"U", format="utf-8")
    def get_unobserved_str(self) -> str:
        return str(self._device.unobserved)

    @_interpreter.command(b"\x02(.{4})", interrupt=True)
    def set_unobserved_bytes(self, value: bytes) -> bytes:
        self._device.unobserved = struct.unpack(">i", value)[0]
        return struct.pack(">i", self._device.unobserved)

    @_interpreter.command(r"U=(\d+\.?\d*)", format="utf-8")
    def set_unobserved_str(self, value: int) -> str:
        self._device.unobserved = value
        return "Unobserved set to {}".format(self._device.unobserved)

    @_interpreter.command(chr(0x1F95A), format="utf-8")
    def misc(self) -> str:
        return chr(0x1F430)
