from dataclasses import dataclass

from aiohttp import web

from tickit.adapters.httpadapter import HttpAdapter
from tickit.adapters.interpreters.endpoints.http_endpoint import HttpEndpoint
from tickit.core.components.component import Component, ComponentConfig
from tickit.core.components.device_simulation import DeviceSimulation
from tickit.devices.iobox import IoBoxDevice


class IoBoxHttpAdapter(HttpAdapter):
    """An adapter for an IoBox that allows reads and writes via REST calls"""

    device: IoBoxDevice

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
        self.device.write(address, new_value)
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
        value = self.device.read(address)
        return web.json_response({address: value})


@dataclass
class ExampleHttpDevice(ComponentConfig):
    """Example HTTP device."""

    host: str = "localhost"
    port: int = 8080

    def __call__(self) -> Component:  # noqa: D102
        return DeviceSimulation(
            name=self.name,
            device=IoBoxDevice(),
            adapters=[IoBoxHttpAdapter(self.host, self.port)],
        )
