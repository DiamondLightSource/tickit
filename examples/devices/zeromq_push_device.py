from dataclasses import dataclass, field
from typing import Optional, Set

from tickit.adapters.zeromq.push_adapter import (
    SocketFactory,
    ZeroMqPushAdapter,
    create_zmq_push_socket,
)
from tickit.core.components.component import Component, ComponentConfig
from tickit.core.components.device_simulation import DeviceSimulation
from tickit.devices.iobox import IoBoxDevice


class IoBoxZeroMqAdapter(ZeroMqPushAdapter):
    """An Eiger adapter which parses the commands sent to the HTTP server."""

    device: IoBoxDevice[str, int]
    _addresses_to_publish: Set[str]

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 5555,
        socket_factory: Optional[SocketFactory] = create_zmq_push_socket,
        addresses_to_publish: Optional[Set[str]] = None,
    ) -> None:
        super().__init__(host, port, socket_factory)
        self._addresses_to_publish = addresses_to_publish or set()

    def after_update(self):
        for address in self._addresses_to_publish:
            value = self.device.read(address)
            self.send_message([{address: value}])


@dataclass
class ExampleZeroMqPusher(ComponentConfig):
    """Device that can publish writes to its memory over a zeromq socket."""

    host: str = "127.0.0.1"
    port: int = 5555
    addresses_to_publish: Set[str] = field(default_factory=lambda: {"foo", "bar"})

    def __call__(self) -> Component:  # noqa: D102
        return DeviceSimulation(
            name=self.name,
            device=IoBoxDevice(),
            adapters=[IoBoxZeroMqAdapter()],
        )
