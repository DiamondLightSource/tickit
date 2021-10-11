from typing import Awaitable, Callable

from aiohttp import web

from tickit.adapters.httpadapter import HTTPAdapter
from tickit.adapters.interpreters.endpoints.http_endpoint import HTTPEndpoint
from tickit.adapters.servers.http_server import HTTPServer
from tickit.core.adapter import ConfigurableAdapter
from tickit.core.device import ConfigurableDevice, DeviceUpdate
from tickit.core.typedefs import SimTime
from tickit.devices.eiger.eiger_settings import EigerSettings
from tickit.utils.byte_format import ByteFormat

from .eiger_status import EigerStatus, State

DETECTOR_API = "detector/api/1.8"


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
        trigger_mode = getattr(self.settings, "trigger_mode")
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

    def update(self, time: SimTime, inputs: Inputs) -> DeviceUpdate[Outputs]:
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

    def get_state(self) -> State:
        """Returns the current state of the Eiger.

        Returns:
            State: The state of the Eiger.
        """
        return getattr(self.status, "state")

    def _set_state(self, state: State):
        # LOGGER.info(f"Transitioned State: [{self.state} -> {state}]")
        setattr(self.status, "state", state)


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
            attr = getattr(self._device.settings, param)
        else:
            attr = None

        return web.Response(text=str(attr))

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

        if self._device.get_state() != State.IDLE:
            return web.Response(text="Eiger not initialized or is currently running.")
        elif (
            hasattr(self._device.settings, param)
            and self._device.get_state() == State.IDLE
        ):
            attr = getattr(self._device.settings, param)

            attr = response["value"]

            setattr(self._device.settings, param, attr)

            return web.Response(
                text="Set: " + str(param) + " to " + str(response["value"])
            )
        else:
            return web.Response(text="Eiger has no config variable: " + str(param))

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
            attr = getattr(self._device.status, param)
        else:
            attr = None

        return web.Response(text=str(attr))

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

        return web.Response(text=str("Initializing Eiger..."))

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

        return web.Response(text=str("Arming Eiger..."))

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

        return web.Response(text=str("Disarming Eiger..."))

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

        return web.Response(text=str(trigger_message))

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

        return web.Response(text=str("Cancelling Eiger..."))

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

        return web.Response(text=str("Aborting Eiger..."))
