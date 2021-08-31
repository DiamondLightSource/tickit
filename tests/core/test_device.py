from dataclasses import is_dataclass
from typing import Optional

import pytest

from tickit.core.device import DeviceConfig, UpdateEvent
from tickit.core.typedefs import SimTime, State


def test_update_event_is_dataclass():
    assert is_dataclass(UpdateEvent)


def test_update_event_has_state():
    assert State == UpdateEvent.__annotations__["state"]


def test_update_event_has_call_in():
    assert Optional[SimTime] == UpdateEvent.__annotations__["call_in"]


def test_device_config_is_dataclass():
    assert is_dataclass(DeviceConfig)


def test_device_config_configures_raises_not_implemented():
    with pytest.raises(NotImplementedError):
        DeviceConfig.configures()


def test_device_config_kwargs_raises_not_implemented():
    device_config = DeviceConfig()
    with pytest.raises(NotImplementedError):
        device_config.kwargs
