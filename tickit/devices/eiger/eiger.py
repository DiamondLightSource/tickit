import logging
from typing import Awaitable, Callable

from aiohttp import web
from apischema import serialize

from tickit.adapters.httpadapter import HTTPAdapter
from tickit.adapters.interpreters.endpoints.http_endpoint import HTTPEndpoint
from tickit.adapters.servers.http_server import HTTPServer
from tickit.core.adapter import ConfigurableAdapter
from tickit.core.device import ConfigurableDevice, DeviceUpdate
from tickit.core.typedefs import SimTime
from tickit.devices.eiger.eiger_schema import AccessMode, SequenceComplete, Value
from tickit.devices.eiger.eiger_settings import EigerSettings
from tickit.utils.byte_format import ByteFormat

from .eiger_status import EigerStatus, State

DETECTOR_API = "detector/api/1.8.0"

LOGGER = logging.getLogger(__name__)


class Eiger(ConfigurableDevice):
    """A device class for the Eiger detector."""

    settings: EigerSettings

    status: EigerStatus

    def __init__(
        self,
    ) -> None:
        """An Eiger device constructor.

        An Eiger device constructor which configures the default settings and various
        states of the device.
        """
        self.settings = EigerSettings()
        self.status = EigerStatus()

    async def initialize(self) -> None:
        """Function to initialise the Eiger."""
        self._set_state(State.IDLE)

    async def arm(self) -> None:
        """Function to arm the Eiger."""
        self._set_state(State.READY)

    async def disarm(self) -> None:
        """Function to disarm the Eiger."""
        self._set_state(State.IDLE)

    async def trigger(self) -> str:
        """Function to trigger the Eiger."""
        trigger_mode = self.settings.trigger_mode
        state = self.status.state

        if state == State.READY and trigger_mode == "ints":
            # If the detector is in an external trigger mode, this is disabled as
            # this software command interface only works for internal triggers.
            self._set_state(State.ACQUIRE)
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

    async def abort(self) -> None:
        """Function to abort the current task on the Eiger."""
        # Do aborting stuff
        self._set_state(State.IDLE)

    def update(self, time: SimTime) -> DeviceUpdate:
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
        # LOGGER.info(f"Transitioned State: [{self.state} -> {state}]")
        self.status.state = state


class EigerAdapter(HTTPAdapter, ConfigurableAdapter):
    """An Eiger adapter which parses the commands sent to the HTTP server."""

    _device: Eiger

    def __init__(
        self,
        device: Eiger,
        raise_interrupt: Callable[[], Awaitable[None]],
        host: str = "localhost",
        port: int = 8080,
    ) -> None:
        """An adapter which instantiates a HTTPServer with configured host and port.

        Args:
            device (Eiger): The Eiger device
            raise_interrupt (Callable): A callback to request that the device is
                updated immediately.
            host (Optional[str]): The host address of the HTTPServer. Defaults to
                "localhost".
            port (Optional[str]): The bound port of the HTTPServer. Defaults to 8080.
        """
        super().__init__(
            device,
            raise_interrupt,
            HTTPServer(host, port, ByteFormat(b"%b\r\n")),
        )

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

        if hasattr(self._device.settings, param):
            attr = self._device.settings[param]

            data = serialize(
                Value(
                    attr["value"],
                    attr["metadata"]["value_type"].value,
                    access_mode=attr["metadata"]["access_mode"].value,
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

        if self._device.get_state()["value"] != State.IDLE.value:
            LOGGER.warn("Eiger not initialized or is currently running.")
            return web.json_response(serialize(SequenceComplete(7)))
        elif (
            hasattr(self._device.settings, param)
            and self._device.get_state()["value"] == State.IDLE.value
        ):
            attr = response["value"]

            LOGGER.debug(f"Changing to {attr} for {param}")

            setattr(self._device.settings, param, attr)

            LOGGER.info("Set: " + str(param) + " to " + str(attr))
            return web.json_response(serialize(SequenceComplete(8)))
        else:
            LOGGER.warn("Eiger has no config variable: " + str(param))
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

        if hasattr(self._device.status, param):
            attr = self._device.status[param]
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
        await self._device.initialize()

        LOGGER.info("Initializing Eiger...")
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
        # Do arming stuff
        await self._device.arm()

        LOGGER.info("Arming Eiger...")
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
        # Do disarming stuff
        await self._device.disarm()

        LOGGER.info("Disarming Eiger...")
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
        # Do triggering stuff
        trigger_message = await self._device.trigger()
        self._device._set_state(State.IDLE)

        LOGGER.info(trigger_message)
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
        # Do disarming stuff
        await self._device.cancel()

        LOGGER.info("Cancelling Eiger...")
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
        # Do disarming stuff
        await self._device.abort()

        LOGGER.info("Aborting Eiger...")
        return web.json_response(serialize(SequenceComplete(6)))