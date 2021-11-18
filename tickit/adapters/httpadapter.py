import asyncio
import logging
from dataclasses import dataclass
from inspect import getmembers
from typing import Iterable

from aiohttp import web
from aiohttp.web_routedef import RouteDef

from tickit.adapters.interpreters.endpoints.http_endpoint import HTTPEndpoint
from tickit.core.adapter import Adapter, RaiseInterrupt
from tickit.core.device import Device

LOGGER = logging.getLogger(__name__)


@dataclass
class HTTPAdapter(Adapter):
    """An adapter implementation which delegates to a server and sets up endpoints.

    An adapter implementation which delegates the hosting of an http requests to a
    server and sets up the endpoints for said server.
    """

    host: str = "localhost"
    port: int = 8080

    async def run_forever(
        self, device: Device, raise_interrupt: RaiseInterrupt
    ) -> None:
        """Runs the server continously."""
        await super().run_forever(device, raise_interrupt)
        LOGGER.debug(f"Starting HTTP server... {self}")
        app = web.Application()
        app.add_routes(list(self.endpoints()))
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host=self.host, port=self.port)
        await site.start()
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            pass
        finally:
            # TODO: This doesn't work yet due to asyncio's own exception handler
            await app.shutdown()
            await app.cleanup()

    def endpoints(self) -> Iterable[RouteDef]:
        """Returns list of endpoints.

        Fetches the defined HTTP endpoints in the device adapter, parses them and
        then yields them.

        Returns:
            Iterable[HTTPEndpoint]: The list of defined endpoints

        Yields:
            Iterator[Iterable[HTTPEndpoint]]: The iterator of the defined endpoints
        """
        for _, func in getmembers(self):
            endpoint: HTTPEndpoint = getattr(func, "__endpoint__", None)
            if endpoint is not None:
                if endpoint.interrupt:
                    old_func = func

                    async def func(*args, **kwargs):
                        await old_func(*args, **kwargs)
                        await self.raise_interrupt()

                yield endpoint.define(func)
