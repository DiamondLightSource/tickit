from dataclasses import is_dataclass
from typing import Optional

from tickit.core.device import DeviceUpdate, OutMap
from tickit.core.typedefs import SimTime


def test_device_update_is_dataclass():
    assert is_dataclass(DeviceUpdate)


def test_device_update_has_state():
    assert OutMap == DeviceUpdate.__annotations__["outputs"]


def test_device_update_has_call_in():
    assert Optional[SimTime] == DeviceUpdate.__annotations__["call_at"]
