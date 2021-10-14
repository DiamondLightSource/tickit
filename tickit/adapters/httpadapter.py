from dataclasses import dataclass
from inspect import getmembers
from typing import Awaitable, Callable, Iterable

from tickit.adapters.interpreters.endpoints.http_endpoint import HTTPEndpoint
from tickit.adapters.servers.http_server import HTTPServer
from tickit.core.device import Device


@dataclass
class HTTPAdapter:
    """An adapter implementation which delegates to a server and sets up endpoints.

    An adapter implementation which delegates the hosting of an http requests to a
    server and sets up the endpoints for said server.
    """

    _device: Device
    _raise_interrupt: Callable[[], Awaitable[None]]
    _server: HTTPServer

    async def run_forever(self) -> None:
        """Runs the server continously."""
        self._server.app.add_routes(list(self.endpoints()))

        await self._server.run_forever()

    def endpoints(self) -> Iterable[HTTPEndpoint]:
        """Returns list of endpoints.

        Fetches the defined HTTP endpoints in the device adapter, parses them and
        then yields them.

        Returns:
            Iterable[HTTPEndpoint]: The list of defined endpoints

        Yields:
            Iterator[Iterable[HTTPEndpoint]]: The iterator of the defined endpoints
        """
        for _, func in getmembers(self):
            endpoint = getattr(func, "__endpoint__", None)
            if endpoint is not None:
                yield endpoint.define(func)
