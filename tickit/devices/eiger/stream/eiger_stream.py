# import asyncio
import logging

from aiohttp import web
from apischema import serialize
from typing_extensions import TypedDict

from tickit.adapters.interpreters.endpoints.http_endpoint import HTTPEndpoint

# from tickit.core.device import Device, DeviceUpdate
from tickit.core.typedefs import SimTime
from tickit.devices.eiger.eiger_schema import Value
from tickit.devices.eiger.stream.stream_config import StreamConfig
from tickit.devices.eiger.stream.stream_status import StreamStatus

# from dataclasses import dataclass


LOGGER = logging.getLogger(__name__)
STREAM_API = "stream/api/1.8.0"


class EigerStream:
    """Simulation of an Eiger stream."""

    # stream_status: StreamStatus = StreamStatus()
    # stream_config: StreamConfig = StreamConfig()
    # # stream_messages: asyncio.Queue = asyncio.Queue()
    # stream_callback_period: SimTime = SimTime(int(1e9))

    #: An empty typed mapping of input values
    Inputs: TypedDict = TypedDict("Inputs", {})
    #: A typed mapping containing the 'value' output value
    Outputs: TypedDict = TypedDict("Outputs", {})

    def __init__(self, callback_period: int = int(1e9)) -> None:
        """An Eiger Stream constructor."""
        self.stream_status = StreamStatus()
        self.stream_config = StreamConfig()
        # self.stream_messages = asyncio.Queue()
        self.stream_callback_period = SimTime(callback_period)

    # def update(self, time: SimTime, inputs: Inputs) -> DeviceUpdate[Outputs]:
    #     """The update method which produces the incremented value.

    #     Args:
    #         time (SimTime): The current simulation time (in nanoseconds).
    #         inputs (State): A mapping of inputs to the device and their values.

    #     Returns:
    #         DeviceUpdate[Outputs]:
    #             The produced update event which contains the incremented value, and
    #             requests a callback of 1s.
    #     """
    #     LOGGER.debug("Stream update...")
    #     return DeviceUpdate(
    #         EigerStream.Outputs(),
    #         SimTime(time + self.stream_callback_period),
    #     )

    def test(self) -> None:
        """[summary]."""
        pass


class EigerStreamAdapter:
    """An adapter for the Stream."""

    device: EigerStream

    @HTTPEndpoint.get(f"/{STREAM_API}" + "/status/{param}")
    async def get_stream_status(self, request: web.Request) -> web.Response:
        """A HTTP Endpoint for requesting status values from the Stream.

        Args:
            request (web.Request): The request object that takes the given parameter.

        Returns:
            web.Response: The response object returned given the result of the HTTP
                request.
        """
        param = request.match_info["param"]
        val = self.device.stream_status[param]["value"]
        meta = self.device.stream_status[param]["metadata"]

        data = serialize(
            Value(val, meta["value_type"].value, access_mode=meta["access_mode"].value)
        )

        return web.json_response(data)

    @HTTPEndpoint.get(f"/{STREAM_API}" + "/config/{param}")
    async def get_stream_config(self, request: web.Request) -> web.Response:
        """A HTTP Endpoint for requesting config values from the Stream.

        Args:
            request (web.Request): The request object that takes the given parameter.

        Returns:
            web.Response: The response object returned given the result of the HTTP
                request.
        """
        param = request.match_info["param"]
        val = self.device.stream_config[param]["value"]
        meta = self.device.stream_config[param]["metadata"]

        data = serialize(
            Value(val, meta["value_type"].value, access_mode=meta["access_mode"].value)
        )

        return web.json_response(data)
