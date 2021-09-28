# import asyncio
from typing import Awaitable, Callable, Optional

from aiohttp import web

from tickit.adapters.httpadapter import HTTPAdapter
from tickit.adapters.interpreters.endpoints.http_endpoint import HTTPEndpoint
from tickit.adapters.servers.http import HTTPServer
from tickit.core.adapter import ConfigurableAdapter
from tickit.core.device import ConfigurableDevice, DeviceUpdate
from tickit.core.typedefs import SimTime
from tickit.utils.byte_format import ByteFormat
from tickit.utils.compat.typing_compat import TypedDict


class Eiger(ConfigurableDevice):

    Inputs: TypedDict = TypedDict("Inputs", {"trigger": bool})

    Outputs: TypedDict = TypedDict("Outputs", {"Current": float})

    def __init__(
        self,
        trigger: bool = False,
        num_images: Optional[int] = 3600,
        block_size: Optional[int] = 1000,
    ) -> None:
        """[summary]

        Args:
            num_images (int, optional): [description]. Defaults to 3600.
            block_size (int, optional): [description]. Defaults to 1000.
        """

        self.trigger = trigger
        self.num_images = num_images
        self.block_size = block_size

    def update(self, time: SimTime, inputs: Inputs) -> DeviceUpdate[Outputs]:
        pass


class EigerAdapter(HTTPAdapter, ConfigurableAdapter):

    _device: Eiger

    def __init__(
        self,
        device: Eiger,
        raise_interrupt: Callable[[], Awaitable[None]],
        host: str = "localhost",
        port: int = 8080,
    ) -> None:

        super().__init__(
            device,
            raise_interrupt,
            HTTPServer(host, port, ByteFormat(b"%b\r\n")),
        )

    @HTTPEndpoint("/command/foo/", method="PUT", name="command")
    async def handle_put(self, request):  # self, data: int) -> str:

        return web.Response(text=str("put data"))

    @HTTPEndpoint("/info/bar/{data}", method="GET", name="info")
    async def handle_get(self, request):  # self, json: Dict[str, Any]) -> None:
        return web.Response(text="Your data: {}".format(request.match_info["data"]))

    # app.add_routes(routes)
