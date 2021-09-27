# import asyncio

# import json
import logging

from aiohttp import web

# from tickit.adapters.interpreters.endpoints.rest_endpoint import RestEndpoint
from tickit.core.adapter import ConfigurableServer
from tickit.utils.byte_format import ByteFormat

# from asyncio.streams import StreamReader, StreamWriter
# from typing import List


LOGGER = logging.getLogger(__name__)

routes = web.RouteTableDef()


class HttpServer(ConfigurableServer):
    """A configurable http server with message handling for use in adapters."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 8080,
        format: ByteFormat = ByteFormat(b"%b"),
    ) -> None:
        """The HttpServer constructor which takes a host, port and format byte string.

        Args:
            host (str): The host name which the server should be run under.
            port (int): The port number which the server should listen to.
            format (ByteFormat): A formatting string for messages sent by the server,
                allowing for the prepending and appending of data. Defaults to b"%b".
        """
        self.host = host
        self.port = port
        self.format = format.format

    async def run_forever(
        self,
        # on_connect: Callable[[], AsyncIterable[bytes]],
        # handler: Callable[[bytes], Awaitable[AsyncIterable[bytes]]],
    ) -> None:
        """Runs the HTTP server indefinitely on the configured host and port.

        An asynchronous method used to run the server indefinitely on the configured
        host and port. Upon client connection, messages from the on_connect iterable
        will be sent. Upon recieving a message the server will delegate handling of it
        to the handler. Replies will be formatted according to the configured format
        string.

        Args:
            on_connect (Callable[[], AsyncIterable[bytes]]): An asynchronous iterable
                of messages to be sent upon client connection.
            handler (Callable[[bytes], Awaitable[AsyncIterable[bytes]]]): An
                asynchronous message handler which returns an asynchronous iterable of
                replies.
        """
        # tasks: List[asyncio.Task] = list()

        @routes.get("/")
        async def handle(request):
            return web.Response(text="Hello world!")

        @routes.put("/command/foo/", name="command")
        async def handle_put(request):  # self, data: int) -> str:

            return web.Response(text=str("put data"))

        @routes.get("/info/bar/{data}", name="info")
        async def handle_get(request):  # self, json: Dict[str, Any]) -> None:
            return web.Response(text="Your data: {}".format(request.match_info["data"]))

        app = web.Application()
        app.add_routes(routes)

        web.run_app(app)
