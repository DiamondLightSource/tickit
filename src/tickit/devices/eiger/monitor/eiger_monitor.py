import logging

from aiohttp import web
from apischema import serialize
from typing_extensions import TypedDict

from tickit.adapters.interpreters.endpoints.http_endpoint import HTTPEndpoint
from tickit.core.typedefs import SimTime
from tickit.devices.eiger.eiger_schema import Value
from tickit.devices.eiger.monitor.monitor_config import MonitorConfig
from tickit.devices.eiger.monitor.monitor_status import MonitorStatus

LOGGER = logging.getLogger(__name__)

MONITOR_API = "monitor/api/1.8.0"


class EigerMonitor:
    """Simulation of an Eiger Monitor."""

    #: An empty typed mapping of input values
    Inputs: TypedDict = TypedDict("Inputs", {})
    #: A typed mapping containing the 'value' output value
    Outputs: TypedDict = TypedDict("Outputs", {})

    def __init__(self) -> None:
        """An Eiger Monitor constructor."""
        self.monitor_status: MonitorStatus = MonitorStatus()
        self.monitor_config: MonitorConfig = MonitorConfig()
        self.monitor_callback_period = SimTime(int(1e9))


class EigerMonitorAdapter:
    """An adapter for the Monitor."""

    device: EigerMonitor

    @HTTPEndpoint.get(f"/{MONITOR_API}" + "/config/{param}")
    async def get_monitor_config(self, request: web.Request) -> web.Response:
        """A HTTP Endpoint for requesting config values from the Monitor.

        Args:
            request (web.Request): The request object that takes the given parameter.

        Returns:
            web.Response: The response object returned given the result of the HTTP
                request.
        """
        param = request.match_info["param"]
        val = self.device.monitor_config[param]["value"]
        meta = self.device.monitor_config[param]["metadata"]

        data = serialize(
            Value(val, meta["value_type"].value, access_mode=meta["access_mode"])
        )

        return web.json_response(data)

    @HTTPEndpoint.get(f"/{MONITOR_API}" + "/status/{param}")
    async def get_monitor_status(self, request: web.Request) -> web.Response:
        """A HTTP Endpoint for requesting status values from the Monitor.

        Args:
            request (web.Request): The request object that takes the given parameter.

        Returns:
            web.Response: The response object returned given the result of the HTTP
                request.
        """
        param = request.match_info["param"]
        val = self.device.monitor_status[param]["value"]
        meta = self.device.monitor_status[param]["metadata"]

        data = serialize(
            Value(val, meta["value_type"].value, access_mode=meta["access_mode"])
        )

        return web.json_response(data)
