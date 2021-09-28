# import json
import asyncio
import logging

# from asyncio.streams import StreamReader, StreamWriter
from typing import AsyncIterable, Awaitable, Callable, List

from aiohttp import web

# from tickit.adapters.interpreters.endpoints.rest_endpoint import RestEndpoint
from tickit.core.adapter import ConfigurableServer
from tickit.utils.byte_format import ByteFormat

LOGGER = logging.getLogger(__name__)


class HTTPServer(ConfigurableServer):
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
        self.app = web.Application()
        self.routes = web.RouteTableDef()

    async def run_forever(
        self,
    ) -> None:
        """Runs the HTTP server indefinitely on the configured host and port.

        An asynchronous method used to run the server indefinitely on the configured
        host and port.

        Args:
            on_connect (Callable[[], AsyncIterable[bytes]]): An asynchronous iterable
                of messages to be sent upon client connection.
            handler (Callable[[bytes], Awaitable[AsyncIterable[bytes]]]): An
                asynchronous message handler which returns an asynchronous iterable of
                replies.
        """

        # @self.routes.get("/")
        # async def handle(request):
        #     return web.Response(text="Hello world!")

        # self.app.add_routes(self.routes)

        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, host=self.host, port=self.port)
        await site.start()

        await asyncio.Event().wait()

    async def shutdown(server, handler, app):
        server.close()
        await server.wait_closed()
        app.client.close()  # db connection closed
        await app.shutdown()
        await handler.finish_connections(10.0)
        await app.cleanup()
