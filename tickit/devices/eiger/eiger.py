from typing import Awaitable, Callable, Optional

from aiohttp import web

from tickit.adapters.httpadapter import HTTPAdapter
from tickit.adapters.interpreters.endpoints.http_endpoint import HTTPEndpoint
from tickit.adapters.servers.http_server import HTTPServer
from tickit.core.adapter import ConfigurableAdapter
from tickit.core.device import ConfigurableDevice, DeviceUpdate
from tickit.core.typedefs import SimTime
from tickit.devices.eiger.eiger_settings import EigerSettings
from tickit.utils.byte_format import ByteFormat
from tickit.utils.compat.typing_compat import TypedDict


class Eiger(ConfigurableDevice):
    """A device class for the Eiger detector.

    ...
    """

    Inputs: TypedDict = TypedDict("Inputs", {"foo": bool})

    Outputs: TypedDict = TypedDict("Outputs", {"bar": float})

    settings: EigerSettings

    def __init__(
        self,
        foo: float = 0.5,
        bar: Optional[int] = 10,
    ) -> None:
        """An example HTTP device constructor which configures the ... .

        Args:
            foo (bool): A flag to indicate something. Defauls to False.
            bar (int, optional): A number to represent something. Defaults to 3600.
        """
        self.foo = foo
        self.bar = bar
        self.settings = EigerSettings()

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


class EigerAdapter(HTTPAdapter, ConfigurableAdapter):
    """An Eiger adapter which parses the commands sent to the HTTP server."""

    _device: Eiger

    def __init__(
        self,
        device: Eiger,
        raise_interrupt: Callable[[], Awaitable[None]],
        host: str = "localhost",
        port: int = 8080,
    ) -> None:
        """An adapter which instantiates a HTTPServer with configured host and port.

        Args:
            device (Eiger): The Eiger device
            raise_interrupt (Callable): A callback to request that the device is
                updated immediately.
            host (Optional[str]): The host address of the HTTPServer. Defaults to
                "localhost".
            port (Optional[str]): The bound port of the HTTPServer. Defaults to 8080.
        """
        super().__init__(
            device,
            raise_interrupt,
            HTTPServer(host, port, ByteFormat(b"%b\r\n")),
        )

    # TODO: Make API version setable in the config params?
    @HTTPEndpoint.get("/detector/api/1.8/config/{parameter_name}")
    async def get_config(self, request: web.Request) -> web.Response:
        """A HTTP Endpoint for requesting configuration variables from the Eiger.

        Args:
            request (web.Request): The request object that takes the given parameter.

        Returns:
            web.Response: The response object returned given the result of the HTTP
                request.
        """
        param = request.match_info["parameter_name"]

        try:
            attr = getattr(self._device.settings, param)
        except AttributeError:
            attr = None
        finally:
            return web.Response(text=str(attr))

    @HTTPEndpoint.put("/detector/api/1.8/config/{parameter_name}", include_json=True)
    async def put_config(self, request: web.Request) -> web.Response:
        """A HTTP Endpoint for setting configuration variables for the Eiger.

        Args:
            request (web.Request): The request object that takes the given parameter
            and value.

        Returns:
            web.Response: The response object returned given the result of the HTTP
                request.
        """
        param = request.match_info["parameter_name"]

        response = await request.json()

        try:
            attr = getattr(self._device.settings, param)

            attr["value"] = response["value"]

            setattr(self._device.settings, param, attr)
        except AttributeError:
            pass
        finally:
            return web.Response(
                text="Set: " + str(param) + " to " + str(response["value"])
            )
