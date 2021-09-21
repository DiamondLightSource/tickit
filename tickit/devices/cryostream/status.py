import struct
from dataclasses import dataclass


@dataclass
class Status:
    """Dataclass containing the status data of a Cryostream object."""

    length: int
    type_status: int
    gas_set_point: int
    gas_temp: int
    gas_error: int
    run_mode: int
    phase_id: int
    ramp_rate: int
    target_temp: int
    evap_temp: int
    suct_temp: int
    remaining: int
    gas_flow: int
    gas_heat: int
    evap_heat: int
    suct_heat: int
    line_pressure: int
    alarm_code: int
    run_time: int
    controller_number: int
    software_version: int
    evap_adjust: int
    status_bytes_string: str = ">BBHHhBBHHHHHBBBBBBHHBB"

    def pack(self) -> bytes:
        """Converts the status data into a bytes object."""
        status_bytes = struct.pack(
            self.status_bytes_string,
            self.length,
            self.type_status,
            self.gas_set_point,
            self.gas_temp,
            self.gas_error,
            self.run_mode,
            self.phase_id,
            self.ramp_rate,
            self.target_temp,
            self.evap_temp,
            self.suct_temp,
            self.remaining,
            self.gas_flow,
            self.gas_heat,
            self.evap_heat,
            self.suct_heat,
            self.line_pressure,
            self.alarm_code,
            self.run_time,
            self.controller_number,
            self.software_version,
            self.evap_adjust,
        )

        return status_bytes


@dataclass
class ExtendedStatus:
    """Dataclass containing the extended status data for a CryoStream object.

    Chars have a size of 1 byte, shorts have a size of 2 bytes
    All temperatures are in centi-Kelvin 80K is reported as 8000
    """

    length: int
    type_status: int
    gas_set_point: int
    gas_temp: int
    gas_error: int
    run_mode: int
    phase_id: int
    ramp_rate: int
    target_temp: int
    evap_temp: int
    suct_temp: int
    remaining: int
    gas_flow: int
    gas_heat: int
    evap_heat: int
    suct_heat: int
    line_pressure: int
    alarm_code: int
    run_time: int
    controller_number: int
    software_version: int
    evap_adjust: int
    turbo_mode: int
    hardware_type: int
    shutter_state: int  # 800 series do not support CryoShutter
    shutter_time: int  # 800 series do not support CryoShutter
    avg_gas_heat: int
    avg_suct_heat: int
    time_to_fill: int
    total_hours: int
    extended_packet_string: str = ">BBHHhBBHHHHHBBBBBBHHBBBBBBBBHH"

    def pack(self) -> bytes:
        """Converts the status data into a bytes object."""
        extended_status_bytes = struct.pack(
            self.extended_packet_string,
            self.length,
            self.type_status,
            self.gas_set_point,
            self.gas_temp,
            self.gas_error,
            self.run_mode,
            self.phase_id,
            self.ramp_rate,
            self.target_temp,
            self.evap_temp,
            self.suct_temp,
            self.remaining,
            self.gas_flow,
            self.gas_heat,
            self.evap_heat,
            self.suct_heat,
            self.line_pressure,
            self.alarm_code,
            self.run_time,
            self.controller_number,
            self.software_version,
            self.evap_adjust,
            self.turbo_mode,
            self.hardware_type,
            self.shutter_state,
            self.shutter_time,
            self.avg_gas_heat,
            self.avg_suct_heat,
            self.time_to_fill,
            self.total_hours,
        )
        return extended_status_bytes
