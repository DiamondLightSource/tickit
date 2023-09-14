import pydantic.v1.dataclasses
from aiohttp import web

from tickit.adapters.http import HttpAdapter
from tickit.adapters.io.http_io import HttpIo
from tickit.adapters.specifications import HttpEndpoint
from tickit.core.adapter import AdapterContainer
from tickit.core.components.component import Component, ComponentConfig
from tickit.core.components.device_component import DeviceComponent
from tickit.devices.iobox import IoBoxDevice


class IoBoxHttpAdapter(HttpAdapter):
    """An adapter for an IoBox that allows reads and writes via REST calls"""

    io_box: IoBoxDevice

    def __init__(self, io_box: IoBoxDevice) -> None:
        self.io_box = io_box

    @HttpEndpoint.put("/memory/{address}", interrupt=True)
    async def write_to_address(self, request: web.Request) -> web.Response:
        """A HTTP endpoint for sending a command to the example HTTP device.

        Args:
            request (web.Request): [description]

        Returns:
            web.Response: [description]
        """
        address = request.match_info["address"]
        new_value = (await request.json())["value"]
        self.io_box.write(address, new_value)
        return web.json_response({address: new_value})

    @HttpEndpoint.get("/memory/{address}")
    async def read_from_address(self, request: web.Request) -> web.Response:
        """A HTTP endpoint for requesting data from the example HTTP device.

        Args:
            request (web.Request): [description]

        Returns:
            web.Response: [description]
        """
        address = request.match_info["address"]
        value = self.io_box.read(address)
        return web.json_response({address: value})


@pydantic.v1.dataclasses.dataclass
class ExampleHttpDevice(ComponentConfig):
    """Example HTTP device."""

    host: str = "localhost"
    port: int = 8080

    def __call__(self) -> Component:  # noqa: D102
        device = IoBoxDevice()
        adapters = [
            AdapterContainer(
                IoBoxHttpAdapter(device),
                HttpIo(
                    self.host,
                    self.port,
                ),
            )
        ]
        return DeviceComponent(
            name=self.name,
            device=device,
            adapters=adapters,
        )
