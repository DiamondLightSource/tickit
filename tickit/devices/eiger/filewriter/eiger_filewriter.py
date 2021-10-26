import logging
from dataclasses import dataclass

from aiohttp import web
from apischema import serialize
from typing_extensions import TypedDict

from tickit.adapters.interpreters.endpoints.http_endpoint import HTTPEndpoint

# from tickit.adapters.zmqadapter import ZeroMQAdapter
# from tickit.core.device import Device, DeviceUpdate
from tickit.core.typedefs import SimTime
from tickit.devices.eiger.eiger_schema import Value
from tickit.devices.eiger.filewriter.filewriter_config import FileWriterConfig
from tickit.devices.eiger.filewriter.filewriter_status import FileWriterStatus

LOGGER = logging.getLogger(__name__)

FILEWRITER_API = "filewriter/api/1.8.0"


@dataclass
class EigerFileWriter:
    """Simulation of an Eiger monitor."""

    filewriter_status: FileWriterStatus = FileWriterStatus()
    filewriter_config: FileWriterConfig = FileWriterConfig()
    filewriter_callback_period = SimTime(int(1e9))

    #: An empty typed mapping of input values
    Inputs: TypedDict = TypedDict("Inputs", {})
    #: A typed mapping containing the 'value' output value
    Outputs: TypedDict = TypedDict("Outputs", {})


class EigerFileWriterAdapter:
    """An adapter for the Monitor."""

    device: EigerFileWriter

    @HTTPEndpoint.get(f"/{FILEWRITER_API}" + "/config/{param}")
    async def get_filewriter_config(self, request: web.Request) -> web.Response:
        """A HTTP Endpoint for requesting config values from the Filewriter.

        Args:
            request (web.Request): The request object that takes the given parameter.

        Returns:
            web.Response: The response object returned given the result of the HTTP
                request.
        """
        param = request.match_info["param"]
        val = self.device.filewriter_config[param]["value"]
        meta = self.device.filewriter_config[param]["metadata"]

        data = serialize(
            Value(val, meta["value_type"].value, access_mode=meta["access_mode"].value)
        )

        return web.json_response(data)

    @HTTPEndpoint.get(f"/{FILEWRITER_API}" + "/status/{param}")
    async def get_filewriter_status(self, request: web.Request) -> web.Response:
        """A HTTP Endpoint for requesting status values from the Filewriter.

        Args:
            request (web.Request): The request object that takes the given parameter.

        Returns:
            web.Response: The response object returned given the result of the HTTP
                request.
        """
        param = request.match_info["param"]
        val = self.device.filewriter_status[param]["value"]
        meta = self.device.filewriter_status[param]["metadata"]

        data = serialize(
            Value(val, meta["value_type"].value, access_mode=meta["access_mode"].value)
        )

        return web.json_response(data)
