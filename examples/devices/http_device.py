from dataclasses import dataclass
from typing import Optional

from aiohttp import web

from tickit.adapters.httpadapter import HTTPAdapter
from tickit.adapters.interpreters.endpoints.http_endpoint import HTTPEndpoint
from tickit.core.components.component import Component, ComponentConfig
from tickit.core.components.device_simulation import DeviceSimulation
from tickit.core.device import Device, DeviceUpdate
from tickit.core.typedefs import SimTime
from tickit.utils.compat.typing_compat import TypedDict


class ExampleHTTPDevice(Device):
    """A device class for an example HTTP device.

    ...
    """

    Inputs: TypedDict = TypedDict("Inputs", {"foo": bool})

    Outputs: TypedDict = TypedDict("Outputs", {"bar": float})

    def __init__(
        self,
        foo: bool = False,
        bar: Optional[int] = 10,
    ) -> None:
        """An example HTTP device constructor which configures the ... .

        Args:
            foo (bool): A flag to indicate something. Defauls to False.
            bar (int, optional): A number to represent something. Defaults to 3600.
        """
        self.foo = foo
        self.bar = bar

    def update(self, time: SimTime, inputs: Inputs) -> DeviceUpdate[Outputs]:
        """Generic update function to update the values of the ExampleHTTPDevice.

        Args:
            time (SimTime): The simulation time in nanoseconds.
            inputs (Inputs): A TypedDict of the inputs to the ExampleHTTPDevice.

        Returns:
            DeviceUpdate[Outputs]:
                The produced update event which contains the value of the device
                variables.
        """
        pass


class ExampleHTTPAdapter(HTTPAdapter):
    """An Eiger adapter which parses the commands sent to the HTTP server."""

    device: ExampleHTTPDevice

    @HTTPEndpoint.put("/command/foo/")
    async def foo(self, request: web.Request) -> web.Response:
        """A HTTP endpoint for sending a command to the example HTTP device.

        Args:
            request (web.Request): [description]

        Returns:
            web.Response: [description]
        """
        return web.Response(text=str("put data"))

    @HTTPEndpoint.get("/info/bar/{data}")
    async def bar(self, request: web.Request) -> web.Response:
        """A HTTP endpoint for requesting data from the example HTTP device.

        Args:
            request (web.Request): [description]

        Returns:
            web.Response: [description]
        """
        return web.Response(text=f"Your data: {request.match_info['data']}")


@dataclass
class ExampleHTTP(ComponentConfig):
    """Example HTTP device."""

    foo: bool = False
    bar: Optional[int] = 10

    def __call__(self) -> Component:  # noqa: D102
        return DeviceSimulation(
            name=self.name,
            device=ExampleHTTPDevice(foo=self.foo, bar=self.bar),
            adapters=[ExampleHTTPAdapter()],
        )
