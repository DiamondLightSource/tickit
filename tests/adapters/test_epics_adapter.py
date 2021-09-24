from dataclasses import is_dataclass

import pytest
from mock import MagicMock, Mock, create_autospec

from tickit.adapters.epicsadapter import EpicsAdapter
from tickit.core.adapter import ConfigurableAdapter, Interpreter
from tickit.core.device import Device


@pytest.fixture
def MockDevice() -> Mock:
    return create_autospec(Device, instance=False)


@pytest.fixture
def MockInterpreter() -> Mock:
    return MagicMock(Interpreter, instance=True)


def test_epics_adapter_is_configurable_adapter():
    assert issubclass(EpicsAdapter, ConfigurableAdapter)


def test_epics_adapter_configures_dataclass():
    assert is_dataclass(EpicsAdapter.EpicsAdapterConfig)


def test_epics_adapter_config_configures_epics_adapter():
    assert EpicsAdapter.EpicsAdapterConfig.configures() is EpicsAdapter


def test_epics_adapter_constuctor():
    EpicsAdapter("db_file", "ioc_name")


def test_epics_adapter_interrupt_records_empty_on_construct():
    with pytest.raises(AttributeError):
        EpicsAdapter.interrupt_records
