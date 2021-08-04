from dataclasses import is_dataclass
from typing import Dict, List, Optional, Tuple

import pytest

from tickit.core.adapter import AdapterConfig
from tickit.core.device import DeviceConfig, UpdateEvent
from tickit.core.typedefs import DeviceID, IoId, SimTime, State


def test_update_event_is_dataclass():
    assert is_dataclass(UpdateEvent)


def test_update_event_has_state():
    assert State == UpdateEvent.__annotations__["state"]


def test_update_event_has_call_in():
    assert Optional[SimTime] == UpdateEvent.__annotations__["call_in"]


def test_device_config_is_dataclass():
    assert is_dataclass(DeviceConfig)


def test_device_config_has_name():
    assert DeviceID == DeviceConfig.__annotations__["name"]


def test_device_config_has_adapters():
    assert List[AdapterConfig] == DeviceConfig.__annotations__["adapters"]


def test_device_config_has_inputs():
    assert Dict[IoId, Tuple[DeviceID, IoId]] == DeviceConfig.__annotations__["inputs"]


def test_device_config_configures_raises_not_implemented():
    with pytest.raises(NotImplementedError):
        DeviceConfig.configures()


def test_device_config_kwargs_raises_not_implemented():
    device_config = DeviceConfig("TestDevice", list(), dict())
    with pytest.raises(NotImplementedError):
        device_config.__kwargs__
