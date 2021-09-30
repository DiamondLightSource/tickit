import sys
from dataclasses import is_dataclass

import pytest
from mock import MagicMock, Mock, create_autospec
from mock.mock import mock_open, patch

from tickit.core.adapter import ConfigurableAdapter, Interpreter
from tickit.core.device import Device

# % % % % % % % % % % WARNING % % % % % % % % % %
# sys.modules["softioc"] = Mock() must be located
# above the import of tickit.adapters.epicsadapter
sys.modules["softioc"] = Mock()
from tickit.adapters.epicsadapter import (  # noqa; isort:skip
    EpicsAdapter,
    InputRecord,
    softioc,
)


@pytest.fixture
def MockDevice() -> Mock:
    return create_autospec(Device, instance=False)


@pytest.fixture
def MockInterpreter() -> Mock:
    return MagicMock(Interpreter, instance=True)


@pytest.fixture
def epics_adapter() -> EpicsAdapter:
    return EpicsAdapter("db_file", "ioc_name")


@pytest.fixture
def input_record() -> InputRecord:
    def setter():
        return None

    def getter():
        return False

    return InputRecord("input", Mock(setter), Mock(getter))


def test_epics_adapter_is_configurable_adapter():
    assert issubclass(EpicsAdapter, ConfigurableAdapter)


def test_epics_adapter_configures_dataclass():
    assert is_dataclass(EpicsAdapter.EpicsAdapterConfig)


def test_epics_adapter_config_configures_epics_adapter():
    assert EpicsAdapter.EpicsAdapterConfig.configures() is EpicsAdapter


def test_epics_adapter_constuctor(epics_adapter: EpicsAdapter):
    pass


def test_epics_adapter_interrupt_records_empty_on_construct():
    with pytest.raises(AttributeError):
        EpicsAdapter.interrupt_records


def test_link_input_on_interrupt(
    epics_adapter: EpicsAdapter, input_record: InputRecord
):
    def getter():
        return False

    getter = Mock(getter)
    epics_adapter.interrupt_records = {}
    epics_adapter.link_input_on_interrupt(input_record, getter)
    assert epics_adapter.interrupt_records[input_record] == getter


def test_epics_adapter_after_update_method(
    epics_adapter: EpicsAdapter, input_record: InputRecord
):
    def getter():
        return False

    getter = Mock(getter)
    epics_adapter.interrupt_records = {}
    epics_adapter.interrupt_records[input_record] = getter

    epics_adapter.after_update()

    input_record.set.assert_called()


def test_epics_adapter_on_db_load_method(epics_adapter: EpicsAdapter):
    with pytest.raises(NotImplementedError):
        epics_adapter.on_db_load()


def test_epics_adapter_build_ioc_method(epics_adapter: EpicsAdapter):

    epics_adapter.on_db_load = Mock()

    data = b"""record(ao, "$(device):GAIN") {
  field(DTYP, "Hy8001")
  field(OMSL, "supervisory")
  field(OUT, "#C1 S0 @")
  field(DESC, "Gain value")
  field(EGU, "A")
}"""

    expected = b"""record(ao, "$(device):GAIN") {
  field(OMSL, "supervisory")
  field(OUT, "#C1 S0 @")
  field(DESC, "Gain value")
  field(EGU, "A")
}"""

    with patch("builtins.open", mock_open(read_data=data)) as mock_f:  # noqa
        with patch("os.unlink") as mock_unlink:
            epics_adapter.build_ioc()

    unlink_args = mock_unlink.call_args.args
    out_filename = unlink_args[0]

    written_data = open(out_filename, "rb").read()

    assert str(written_data).strip() == str(expected).strip()
    softioc.iocInit.assert_called()
