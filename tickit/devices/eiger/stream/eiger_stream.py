from dataclasses import dataclass, field

from aiohttp import web
from apischema import serialize

from tickit.adapters.interpreters.endpoints.http_endpoint import HTTPEndpoint
from tickit.adapters.zmqadapter import ZeroMQAdapter
from tickit.devices.eiger.eiger_schema import AccessMode, Value
from tickit.devices.eiger.stream.stream_config import StreamConfig
from tickit.devices.eiger.stream.stream_status import StreamStatus

STREAM_API = "stream/api/1.8.0"


@dataclass
class EigerStream:
    """Simulation of an Eiger stream."""

    status: StreamStatus = field(default_factory=StreamStatus)
    config: StreamConfig = field(default_factory=StreamConfig)
    # messages: asyncio.Queue = field(default_factory=asyncio.Queue)


class EigerStreamAdapter(ZeroMQAdapter):
    """An adapter for the Stream."""

    _stream: EigerStream

    @HTTPEndpoint.get(f"/{STREAM_API}" + "/status/dropped")
    async def get_dropped(self, request: web.Request) -> web.Response:
        """A HTTP Endpoint for requesting dropped status from the Stream.

        Args:
            request (web.Request): The request object that takes the given parameter.

        Returns:
            web.Response: The response object returned given the result of the HTTP
                request.
        """
        dropped = self._stream.status["dropped"]
        data = serialize(
            Value(dropped, AccessMode.INT, access_mode=AccessMode.READ_ONLY)
        )

        return web.json_response(data)

    @HTTPEndpoint.get(f"/{STREAM_API}" + "/config/mode")
    async def get_mode(self, request: web.Request) -> web.Response:
        """A HTTP Endpoint for requesting stream mode from the Stream.

        Args:
            request (web.Request): The request object that takes the given parameter.

        Returns:
            web.Response: The response object returned given the result of the HTTP
                request.
        """
        mode = self._stream.config["mode"]
        data = serialize(
            Value(mode, AccessMode.STRING, access_mode=AccessMode.READ_WRITE)
        )

        return web.json_response(data)
