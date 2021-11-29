import logging
from dataclasses import fields
from datetime import datetime, timezone

from typing_extensions import TypedDict

from tickit.core.device import Device, DeviceUpdate
from tickit.core.typedefs import SimTime
from tickit.devices.eiger.data.dummy_image import Image
from tickit.devices.eiger.eiger_schema import Value, construct_value
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

    _num_frames_left: int

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

        self._num_frames_left = 0
        self._series_id = 0

    async def initialize(self) -> None:
        """Function to initialise the Eiger."""
        self._set_state(State.IDLE)

    async def arm(self) -> None:
        """Function to arm the Eiger."""
        self._set_state(State.READY)

        self._series_id += 1

        jsons = []

        header_detail = self.stream_config["header_detail"]["value"]

        header_json = {
            "htype": "dheader-1.0",
            "series": self._series_id,
            "header_detail": header_detail,
        }
        jsons.append(header_json)

        if header_detail != "none":
            config_json = {}
            disallowed_configs = ["flatfield", "pixelmask" "countrate_correction_table"]
            for field_ in fields(self.settings):
                if field_.name not in disallowed_configs:
                    config_json[field_.name] = vars(self.settings)[field_.name]

            jsons.append(config_json)

            if header_detail == "all":
                flatfield_header = {
                    "htype": "flatfield-1.0",
                    "shape": "[x,y]",
                    "type": "float32",
                }
                jsons.append(flatfield_header)
                flatfield_data_blob = {"blob": "blob"}
                jsons.append(flatfield_data_blob)

                pixel_mask_header = {
                    "htype": "dpixelmask-1.0",
                    "shape": "[x,y]",
                    "type": "uint32",
                }
                jsons.append(pixel_mask_header)
                pixel_mask_data_blob = {"blob": "blob"}
                jsons.append(pixel_mask_data_blob)

                countrate_table_header = {
                    "htype": "dcountrate_table-1.0",
                    "shape": "[x,y]",
                    "type": "float32",
                }
                jsons.append(countrate_table_header)
                countrate_table_data_blob = {"blob": "blob"}
                jsons.append(countrate_table_data_blob)

        for json_ in jsons:
            LOGGER.debug(json_)

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
            self._num_frames_left = self.settings.nimages

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

        header_json = {"htype": "dseries_end-1.0", "series": self._series_id}

        LOGGER.debug(header_json)

    async def abort(self) -> None:
        """Function to abort the current task on the Eiger."""
        self._set_state(State.IDLE)

        header_json = {"htype": "dseries_end-1.0", "series": self._series_id}

        LOGGER.debug(header_json)

    def update(self, time: SimTime, inputs: Inputs) -> DeviceUpdate[Outputs]:
        """Update function to update the Eiger.

        Args:
            time (SimTime): The simulation time in nanoseconds.
            inputs (Inputs): A TypedDict of the inputs to the Eiger device.

        Returns:
            DeviceUpdate[Outputs]:
                The produced update event which contains the value of the device
                variables.
        """
        if self.status.state == State.ACQUIRE:
            if self._num_frames_left > 0:

                aquired = Image.create_dummy_image(self._num_frames_left)

                now = datetime.now(timezone.utc).timestamp()

                header_json = {
                    "htype": "dimage-1.0",
                    "series": self._series_id,
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
                    "start_time": now,
                    "stop_time": now + self.settings.frame_time,
                    "real_time": now,
                }

                LOGGER.debug(header_json)
                LOGGER.debug(json2)
                LOGGER.debug(json3)

                self._num_frames_left -= 1

                # Call update() again when time to take the next frame
                return DeviceUpdate(self.Outputs(), self.settings.frame_time)

            else:
                self._set_state(State.IDLE)

        return DeviceUpdate(self.Outputs(), None)

    def get_state(self) -> Value:
        """Returns the current state of the Eiger.

        Returns:
            State: The state of the Eiger.
        """
        state = construct_value(self.status, "state")

        return state

    def _set_state(self, state: State):
        self.status.state = state
