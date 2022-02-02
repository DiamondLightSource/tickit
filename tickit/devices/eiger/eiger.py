import logging
from dataclasses import fields

from apischema import serialize
from typing_extensions import TypedDict

from tickit.core.device import Device, DeviceUpdate
from tickit.core.typedefs import SimTime
from tickit.devices.eiger.data.dummy_image import Image
from tickit.devices.eiger.eiger_schema import AccessMode, Value
from tickit.devices.eiger.eiger_settings import EigerSettings
from tickit.devices.eiger.filewriter.filewriter_config import FileWriterConfig
from tickit.devices.eiger.filewriter.filewriter_status import FileWriterStatus
from tickit.devices.eiger.monitor.monitor_config import MonitorConfig
from tickit.devices.eiger.monitor.monitor_status import MonitorStatus
from tickit.devices.eiger.stream.stream_config import StreamConfig
from tickit.devices.eiger.stream.stream_status import StreamStatus

from .eiger_status import EigerStatus, State

LOGGER = logging.getLogger(__name__)


class EigerDevice(Device):
    """A device class for the Eiger detector."""

    settings: EigerSettings
    status: EigerStatus

    #: An empty typed mapping of input values
    Inputs: TypedDict = TypedDict("Inputs", {"flux": float})
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

        LOGGER.debug(json)
        LOGGER.debug(config_json)

    async def disarm(self) -> None:
        """Function to disarm the Eiger."""
        self._set_state(State.IDLE)

        json = {"htype": "dseries_end-1.0", "series": "<id>"}

        LOGGER.debug(json)

    async def trigger(self) -> str:
        """Function to trigger the Eiger.

        If the detector is in an external trigger mode, this is disabled as
        this software command interface only works for internal triggers.
        """
        trigger_mode = self.settings.trigger_mode
        state = self.status.state

        if state == State.READY and trigger_mode == "ints":
            self._set_state(State.ACQUIRE)

            for idx in range(0, self.settings.nimages):

                aquired = Image.create_dummy_image(idx)

                header_json = {
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

                LOGGER.debug(header_json)
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
        self._set_state(State.READY)

        header_json = {"htype": "dseries_end-1.0", "series": "<id>"}

        LOGGER.debug(header_json)

    async def abort(self) -> None:
        """Function to abort the current task on the Eiger."""
        self._set_state(State.IDLE)

        header_json = {"htype": "dseries_end-1.0", "series": "<id>"}

        LOGGER.debug(header_json)

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
        current_flux = inputs["flux"]

        intensity_scale = (current_flux / 100) * 100
        LOGGER.debug(f"Relative beam intensity: {intensity_scale}")

        return DeviceUpdate(self.Outputs(), None)

    def get_state(self):  # TODO: Add return type hint
        """Returns the current state of the Eiger.

        Returns:
            State: The state of the Eiger.
        """
        val = self.status.state
        allowed = [s.value for s in State]
        return serialize(
            Value(
                val,
                AccessMode.STRING,  # type: ignore
                access_mode=AccessMode.READ_ONLY,
                allowed_values=allowed,
            )
        )

    def _set_state(self, state: State):
        self.status.state = state
