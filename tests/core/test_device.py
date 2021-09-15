from dataclasses import is_dataclass
from typing import Optional

import pytest

from tickit.core.device import DeviceConfig, DeviceUpdate, OutMap
from tickit.core.typedefs import SimTime


def test_device_update_is_dataclass():
    assert is_dataclass(DeviceUpdate)


def test_device_update_has_state():
    assert OutMap == DeviceUpdate.__annotations__["outputs"]


def test_device_update_has_call_in():
    assert Optional[SimTime] == DeviceUpdate.__annotations__["call_at"]


def test_device_config_is_dataclass():
    assert is_dataclass(DeviceConfig)


def test_device_config_configures_raises_not_implemented():
    with pytest.raises(NotImplementedError):
        DeviceConfig.configures()


def test_device_config_kwargs_raises_not_implemented():
    device_config = DeviceConfig()
    with pytest.raises(NotImplementedError):
        device_config.kwargs
