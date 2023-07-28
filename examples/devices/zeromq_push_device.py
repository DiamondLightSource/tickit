import asyncio
from dataclasses import field
from typing import Any, AsyncIterable, Mapping, Optional, Sequence, Set, Union
from pydantic import BaseModel

import pydantic.v1.dataclasses
import zmq
from tickit.adapters.interpreters.zeromq_socket.push_interpreter import (
    ZeroMqPushInterpreter,
)

from tickit.adapters.io.zeromq_push_io import (
    SocketFactory,
    ZeroMqPushIo,
    create_zmq_push_socket,
)
from tickit.core.adapter import AdapterContainer
from tickit.core.components.component import Component, ComponentConfig
from tickit.core.components.device_simulation import DeviceSimulation
from tickit.devices.iobox import IoBoxDevice


class IoBoxZeroMqAdapter(ZeroMqPushInterpreter):
    """An Eiger adapter which parses the commands sent to the HTTP server."""

    device: IoBoxDevice[str, int]
    _addresses_to_publish: Set[str]
    _message_queue: asyncio.Queue

    def __init__(
        self,
        device: IoBoxDevice,
        addresses_to_publish: Optional[Set[str]] = None,
    ) -> None:
        self.device = device
        self._addresses_to_publish = addresses_to_publish or set()
        self._message_queue = asyncio.Queue()

    def after_update(self) -> None:
        for address in self._addresses_to_publish:
            value = self.device.read(address)
            self.add_message_to_stream([{address: value}])


@pydantic.v1.dataclasses.dataclass
class ExampleZeroMqPusher(ComponentConfig):
    """Device that can publish writes to its memory over a zeromq socket."""

    host: str = "127.0.0.1"
    port: int = 5555
    addresses_to_publish: Set[str] = field(default_factory=lambda: {"foo", "bar"})

    def __call__(self) -> Component:  # noqa: D102
        device = IoBoxDevice()
        return DeviceSimulation(
            name=self.name,
            device=device,
            adapters=[
                AdapterContainer(
                    IoBoxZeroMqAdapter(device),
                    ZeroMqPushIo(
                        self.host,
                        self.port,
                        socket_factory=create_zmq_push_socket,
                    ),
                ),
            ],
        )
