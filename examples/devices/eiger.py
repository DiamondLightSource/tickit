# import asyncio
from typing import Awaitable, Callable, Optional

from aiohttp import web

from tickit.adapters.httpadapter import HTTPAdapter
from tickit.adapters.interpreters.endpoints.http_endpoint import HTTPEndpoint
from tickit.adapters.servers.http_server import HTTPServer
from tickit.core.adapter import ConfigurableAdapter
from tickit.core.device import ConfigurableDevice, DeviceUpdate
from tickit.core.typedefs import SimTime
from tickit.utils.byte_format import ByteFormat
from tickit.utils.compat.typing_compat import TypedDict


class Eiger(ConfigurableDevice):
    """A device class for the Eiger detector.

    ...
    """

    Inputs: TypedDict = TypedDict("Inputs", {"trigger": bool})

    Outputs: TypedDict = TypedDict("Outputs", {"Current": float})

    def __init__(
        self,
        trigger: bool = False,
        num_images: Optional[int] = 3600,
        block_size: Optional[int] = 1000,
    ) -> None:
        """An Eiger constructor which configures the ... .

        Args:
            trigger (bool): A flag to indicate whether the Eiger has received a trigger
            signal. Defauls to False.
            num_images (int, optional): The number of images to capture of the
            diffraction pattern of the sample after a trigger signal has been received.
            Defaults to 3600.
            block_size (int, optional): The block size of images each file writer can
            write. Defaults to 1000.
        """
        self.trigger = trigger
        self.num_images = num_images
        self.block_size = block_size

    def update(self, time: SimTime, inputs: Inputs) -> DeviceUpdate[Outputs]:
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
        """An Eiger which instantiates a HTTPServer with configured host and port.

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

    @HTTPEndpoint("/command/foo/", method="PUT", name="command")
    async def foo(self, request) -> web.Response:
        """A HTTP endpoint for sending a command to the Eiger.

        Args:
            request (web.Request): [description]

        Returns:
            web.Response: [description]
        """
        return web.Response(text=str("put data"))

    @HTTPEndpoint("/info/bar/{data}", method="GET", name="info")
    async def bar(self, request) -> web.Response:
        """A HTTP endpoint for requesting data from the Eiger.

        Args:
            request (web.Request): [description]

        Returns:
            web.Response: [description]
        """
        return web.Response(text="Your data: {}".format(request.match_info["data"]))
