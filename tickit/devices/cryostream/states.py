from enum import IntEnum


class RunModes(IntEnum):
    """An enumerator for Cryostream run modes."""

    STARTUP = 0
    STARTUPFAIL = 1
    STARTUPOK = 2
    RUN = 3
    SETUP = 4
    SHUTDOWNOK = 5
    SHUTDOWNFAIL = 6


class PhaseIds(IntEnum):
    """An enumerator for Cryostream phases."""

    RAMP = 0
    COOL = 1
    PLAT = 2
    HOLD = 3
    END = 4
    PURGE = 5


class AlarmCodes(IntEnum):
    """An enumerator for Cryostream alarm codes alarm levels."""

    NO_ERRORS = 0
    STOP_PRESSED = 1
    STOP_COMMAND = 2
    END_COMPLETE = 3
    PURGE_COMPLETE = 4
    TEMP_WARNING = 5
    PRESSURE_WARNING = 6
    CHECK_VACUUM = 7
    SELF_CHECK_FAIL = 8
    FLOW_RATE = 9
    TEMP_CONTROL_ERROR = 10
    GAS_TYPE_ERROR = 11
    TEMP_READING_ERROR = 12
    SUCT_TEMP_ERROR = 13
    SENSOR_FAIL = 14
    BROWNOUT = 15
    SINK_OVERHEAT = 16
    PSU_OVERHEAT = 17
    POWER_LOSS = 18
    COLHEAD_TOO_COLD = 19
    COLHEAD_TIMEOUT = 20
    CRYODRIVE_NOT_FOUND = 21
    CRYODRIVE_ERROR = 22
    NO_NITROGEN = 23
    NO_HELIUM = 24
    VAC_GAUGE_FAIL = 25
    VAC_READING_ERROR = 26
    RS232_ERROR = 27
    COLDHEAD_TEMP_WARNING = 28
    COLDHEAD_TEMP_ERROR = 29
    DO_NOT_OPEN_CRYOSTAT_L2 = 30
    DO_NOT_OPEN_CRYOSTAT_L3 = 31
    UNPLUG_XTAL_SENSOR = 32
    CRYOSTAT_OPEN = 33
    CRYOSTAT_OPEN_TIMEOUT = 34
    HIGH_TEMP_WARNING = 35
    HIGH_TEMP_ERROR = 36
    CRYODRIVE_T_SENSOR_FAULT = 37
    CRYODRIVE_P_SENSOR_FAULT = 38
    CRYODRIVE_LOW_T_TRIP = 39
    CRYODRIVE_HIGH_T_TRIP = 40
    CRYODRIVE_LOW_P_TRIP = 41
    CRYODRIVE_HIGH_T_WARNING = 42
    CRYODRIVE_LOW_P_WARNING = 43
    CONNECT_GAS_SUPPLY = 44
    AUTOFILL_FAULT = 45
    AUTOFILL_ABOUT_TO_FILL = 46
    AUTOFILL_FILLING = 47
    COLLAR_TEMP_ERROR = 48
    COLDHEAD_ERROR = 49
    TURBO_FLOW = 50
    HE_SELECTED = 51
    CRYODRIVE_NOT_READY = 52
    REGEN_REQUIRED = 53
    REGEN_COMPLETE = 54
    CONNECT_VACUUM = 55
    DISCONNECT_VACUUM = 56


class HardwareType(IntEnum):
    """An enumerator for Cryostream hardware types."""

    PLUS_SYSTEM = 1  # Max temp 500 K (Cryostream, Cobra and Smartstream)
    HAS_CRYOSHUTTER = 2  # 700 series Cryostream and Cobra
    SERIES_800 = 3
    HAS_AUTOFILL = 4  # 800 series Cryostream from firmware version 150
