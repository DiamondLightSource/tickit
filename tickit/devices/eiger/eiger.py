import logging
from dataclasses import fields

from aiohttp import web
from apischema import serialize
from typing_extensions import TypedDict

from tickit.adapters.httpadapter import HTTPAdapter
from tickit.adapters.interpreters.endpoints.http_endpoint import HTTPEndpoint
from tickit.adapters.zmqadapter import ZeroMQAdapter
from tickit.core.device import Device, DeviceUpdate
from tickit.core.typedefs import SimTime
from tickit.devices.eiger.data.dummydata import dummy_image
from tickit.devices.eiger.eiger_schema import AccessMode, SequenceComplete, Value
from tickit.devices.eiger.eiger_settings import EigerSettings
from tickit.devices.eiger.filewriter.eiger_filewriter import EigerFileWriterAdapter
from tickit.devices.eiger.filewriter.filewriter_config import FileWriterConfig
from tickit.devices.eiger.filewriter.filewriter_status import FileWriterStatus
from tickit.devices.eiger.monitor.eiger_monitor import EigerMonitorAdapter
from tickit.devices.eiger.monitor.monitor_config import MonitorConfig
from tickit.devices.eiger.monitor.monitor_status import MonitorStatus
from tickit.devices.eiger.stream.eiger_stream import EigerStreamAdapter
from tickit.devices.eiger.stream.stream_config import StreamConfig
from tickit.devices.eiger.stream.stream_status import StreamStatus

from .eiger_status import EigerStatus, State

DETECTOR_API = "detector/api/1.8.0"

LOGGER = logging.getLogger(__name__)


class EigerDevice(Device):
    """A device class for the Eiger detector."""

    settings: EigerSettings
    status: EigerStatus

    #: An empty typed mapping of input values
    Inputs: TypedDict = TypedDict("Inputs", {})
    #: A typed mapping containing the 'value' output value
    Outputs: TypedDict = TypedDict("Outputs", {})

    def __init__(
        self,
    ) -> None:
        """An Eiger device constructor.

        An Eiger device constructor which configures the default settings and various
        states of the device.
        """
        self.settings = EigerSettings()
        self.status = EigerStatus()

        self.stream_status = StreamStatus()
        self.stream_config = StreamConfig()
        self.stream_callback_period = SimTime(int(1e9))

        self.filewriter_status: FileWriterStatus = FileWriterStatus()
        self.filewriter_config: FileWriterConfig = FileWriterConfig()
        self.filewriter_callback_period = SimTime(int(1e9))

        self.monitor_status: MonitorStatus = MonitorStatus()
        self.monitor_config: MonitorConfig = MonitorConfig()
        self.monitor_callback_period = SimTime(int(1e9))

    async def initialize(self) -> None:
        """Function to initialise the Eiger."""
        self._set_state(State.IDLE)

    async def arm(self) -> None:
        """Function to arm the Eiger."""
        self._set_state(State.READY)

        header_detail = self.stream_config["header_detail"]["value"]

        json = {
            "htype": "dheader-1.0",
            "series": "<id>",
            "header_detail": header_detail,
        }
        if header_detail != "none":
            config_json = {}
            disallowed_configs = ["flatfield", "pixelmask" "countrate_correction_table"]
            for field_ in fields(self.settings):
                if field_.name not in disallowed_configs:
                    config_json[field_.name] = vars(self.settings)[field_.name]
                else:
                    continue

        LOGGER.debug(json)
        LOGGER.debug(config_json)

    async def disarm(self) -> None:
        """Function to disarm the Eiger."""
        self._set_state(State.IDLE)

        json = {"htype": "dseries_end-1.0", "series": "<id>"}

        LOGGER.debug(json)

    async def trigger(self) -> str:
        """Function to trigger the Eiger."""
        trigger_mode = self.settings.trigger_mode
        state = self.status.state

        if state == State.READY and trigger_mode == "ints":
            # If the detector is in an external trigger mode, this is disabled as
            # this software command interface only works for internal triggers.
            self._set_state(State.ACQUIRE)

            for i in range(1, self.settings.nimages + 1):

                # "Aquire" an image
                aquired = dummy_image(i)

                json = {
                    "htype": "dimage-1.0",
                    "series": "<series id>",
                    "frame": aquired.index,
                    "hash": aquired.hash,
                }

                json2 = {
                    "htype": "dimage_d-1.0",
                    "shape": "[x,y,(z)]",
                    "type": aquired.dtype,
                    "encoding": aquired.encoding,
                    "size": len(aquired.data),
                }

                json3 = {
                    "htype": "dconfig-1.0",
                    "start_time": "<start_time>",
                    "stop_time": "<stop_time>",
                    "real_time": "<real_time>",
                }

                LOGGER.debug(json)
                LOGGER.debug(json2)
                LOGGER.debug(json3)

            return "Aquiring Data from Eiger..."
        else:
            return (
                f"Ignoring trigger, state={self.status.state},"
                f"trigger_mode={trigger_mode}"
            )

    async def cancel(self) -> None:
        """Function to stop the data acquisition.

        Function to stop the data acquisition, but only after the next
        image is finished.
        """
        # Do data aquisition aborting stuff
        self._set_state(State.READY)

        json = {"htype": "dseries_end-1.0", "series": "<id>"}

        LOGGER.debug(json)

    async def abort(self) -> None:
        """Function to abort the current task on the Eiger."""
        # Do aborting stuff
        self._set_state(State.IDLE)

        json = {"htype": "dseries_end-1.0", "series": "<id>"}

        LOGGER.debug(json)

    def update(self, time: SimTime, inputs) -> DeviceUpdate:
        """Generic update function to update the values of the ExampleHTTPDevice.

        Args:
            time (SimTime): The simulation time in nanoseconds.
            inputs (Inputs): A TypedDict of the inputs to the ExampleHTTPDevice.

        Returns:
            DeviceUpdate[Outputs]:
                The produced update event which contains the value of the device
                variables.
        """
        pass

    def get_state(self) -> Value:
        """Returns the current state of the Eiger.

        Returns:
            State: The state of the Eiger.
        """
        val = self.status.state
        allowed = [s.value for s in State]
        return serialize(
            Value(
                val,
                AccessMode.STRING,
                access_mode=AccessMode.READ_ONLY,
                allowed_values=allowed,
            )
        )

    def _set_state(self, state: State):
        self.status.state = state


class EigerRESTAdapter(
    HTTPAdapter, EigerStreamAdapter, EigerMonitorAdapter, EigerFileWriterAdapter
):
    """An Eiger adapter which parses the commands sent to the HTTP server."""

    device: EigerDevice

    # TODO: Make API version setable in the config params?
    @HTTPEndpoint.get(f"/{DETECTOR_API}" + "/config/{parameter_name}")
    async def get_config(self, request: web.Request) -> web.Response:
        """A HTTP Endpoint for requesting configuration variables from the Eiger.

        Args:
            request (web.Request): The request object that takes the given parameter.

        Returns:
            web.Response: The response object returned given the result of the HTTP
                request.
        """
        param = request.match_info["parameter_name"]

        if hasattr(self.device.settings, param):
            attr = self.device.settings[param]

            data = serialize(
                Value(
                    attr["value"],
                    attr["metadata"]["value_type"].value,
                    access_mode=(
                        attr["metadata"]["access_mode"].value
                        if hasattr(attr["metadata"], "access_mode")
                        else AccessMode.READ_ONLY.value
                    ),
                )
            )
        else:
            data = serialize(Value("None", "string", access_mode="None"))

        return web.json_response(data)

    @HTTPEndpoint.put(
        f"/{DETECTOR_API}" + "/config/{parameter_name}", include_json=True
    )
    async def put_config(self, request: web.Request) -> web.Response:
        """A HTTP Endpoint for setting configuration variables for the Eiger.

        Args:
            request (web.Request): The request object that takes the given parameter
            and value.

        Returns:
            web.Response: The response object returned given the result of the HTTP
                request.
        """
        param = request.match_info["parameter_name"]

        response = await request.json()

        if self.device.get_state()["value"] != State.IDLE.value:
            LOGGER.warning("Eiger not initialized or is currently running.")
            return web.json_response(serialize(SequenceComplete(7)))
        elif (
            hasattr(self.device.settings, param)
            and self.device.get_state()["value"] == State.IDLE.value
        ):
            attr = response["value"]

            LOGGER.debug(f"Changing to {attr} for {param}")

            setattr(self.device.settings, param, attr)

            LOGGER.debug("Set: " + str(param) + " to " + str(attr))
            return web.json_response(serialize(SequenceComplete(8)))
        else:
            LOGGER.warning("Eiger has no config variable: " + str(param))
            return web.json_response(serialize(SequenceComplete(9)))

    @HTTPEndpoint.get(f"/{DETECTOR_API}" + "/status/{status_param}")
    async def get_status(self, request: web.Request) -> web.Response:
        """A HTTP Endpoint for requesting the status of the Eiger.

        Args:
            request (web.Request): The request object that takes the request method.

        Returns:
            web.Response: The response object returned given the result of the HTTP
                request.
        """
        param = request.match_info["status_param"]

        if hasattr(self.device.status, param):
            attr = self.device.status[param]
        else:
            attr = "None"

        data = serialize({"value": attr})

        return web.json_response(data)

    @HTTPEndpoint.get(f"/{DETECTOR_API}" + "/status/board_000/{status_param}")
    async def get_board_000_status(self, request: web.Request) -> web.Response:
        """A HTTP Endpoint for requesting the status of the Eiger.

        Args:
            request (web.Request): The request object that takes the request method.

        Returns:
            web.Response: The response object returned given the result of the HTTP
                request.
        """
        param = request.match_info["status_param"]

        if hasattr(self.device.status, param):
            attr = self.device.status[param]
        else:
            attr = "None"

        data = serialize({"value": attr})

        return web.json_response(data)

    @HTTPEndpoint.get(f"/{DETECTOR_API}" + "/status/builder/{status_param}")
    async def get_builder_status(self, request: web.Request) -> web.Response:
        """A HTTP Endpoint for requesting the status of the Eiger.

        Args:
            request (web.Request): The request object that takes the request method.

        Returns:
            web.Response: The response object returned given the result of the HTTP
                request.
        """
        param = request.match_info["status_param"]

        if hasattr(self.device.status, param):
            attr = self.device.status[param]
        else:
            attr = "None"

        data = serialize({"value": attr})

        return web.json_response(data)

    @HTTPEndpoint.put(f"/{DETECTOR_API}" + "/command/initialize")
    async def initialize_eiger(self, request: web.Request) -> web.Response:
        """A HTTP Endpoint for the 'initialize' command of the Eiger.

        Args:
            request (web.Request): The request object that takes the request method.

        Returns:
            web.Response: The response object returned given the result of the HTTP
                request.
        """
        await self.device.initialize()

        LOGGER.debug("Initializing Eiger...")
        return web.json_response(serialize(SequenceComplete(1)))

    @HTTPEndpoint.put(f"/{DETECTOR_API}" + "/command/arm")
    async def arm_eiger(self, request: web.Request) -> web.Response:
        """A HTTP Endpoint for the 'arm' command of the Eiger.

        Args:
            request (web.Request): The request object that takes the request method.

        Returns:
            web.Response: The response object returned given the result of the HTTP
                request.
        """
        await self.device.arm()

        LOGGER.debug("Arming Eiger...")
        return web.json_response(serialize(SequenceComplete(2)))

    @HTTPEndpoint.put(f"/{DETECTOR_API}" + "/command/disarm")
    async def disarm_eiger(self, request: web.Request) -> web.Response:
        """A HTTP Endpoint for the 'disarm' command of the Eiger.

        Args:
            request (web.Request): The request object that takes the request method.

        Returns:
            web.Response: The response object returned given the result of the HTTP
                request.
        """
        await self.device.disarm()

        LOGGER.debug("Disarming Eiger...")
        return web.json_response(serialize(SequenceComplete(3)))

    @HTTPEndpoint.put(f"/{DETECTOR_API}" + "/command/trigger")
    async def trigger_eiger(self, request: web.Request) -> web.Response:
        """A HTTP Endpoint for the 'trigger' command of the Eiger.

        Args:
            request (web.Request): The request object that takes the request method.

        Returns:
            web.Response: The response object returned given the result of the HTTP
                request.
        """
        trigger_message = await self.device.trigger()
        self.device._set_state(State.IDLE)

        LOGGER.debug(trigger_message)
        return web.json_response(serialize(SequenceComplete(4)))

    @HTTPEndpoint.put(f"/{DETECTOR_API}" + "/command/cancel")
    async def cancel_eiger(self, request: web.Request) -> web.Response:
        """A HTTP Endpoint for the 'cancel' command of the Eiger.

        Args:
            request (web.Request): The request object that takes the request method.

        Returns:
            web.Response: The response object returned given the result of the HTTP
                request.
        """
        await self.device.cancel()

        LOGGER.debug("Cancelling Eiger...")
        return web.json_response(serialize(SequenceComplete(5)))

    @HTTPEndpoint.put(f"/{DETECTOR_API}" + "/command/abort")
    async def abort_eiger(self, request: web.Request) -> web.Response:
        """A HTTP Endpoint for the 'abort' command of the Eiger.

        Args:
            request (web.Request): The request object that takes the request method.

        Returns:
            web.Response: The response object returned given the result of the HTTP
                request.
        """
        await self.device.abort()

        LOGGER.debug("Aborting Eiger...")
        return web.json_response(serialize(SequenceComplete(6)))


class EigerZMQAdapter(ZeroMQAdapter):
    """An Eiger adapter which parses the datato send along a ZeroMQStream."""

    device: EigerDevice
