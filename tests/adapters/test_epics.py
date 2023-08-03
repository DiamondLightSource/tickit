from typing import cast

import pytest
from mock import Mock

from tickit.adapters.epics import EpicsAdapter, InputRecord


@pytest.fixture
def epics_adapter() -> EpicsAdapter:
    return EpicsAdapter()


@pytest.fixture
def input_record() -> InputRecord:
    def setter():
        return None

    def getter():
        return False

    return InputRecord("input", Mock(setter), Mock(getter))


def test_epics_adapter_interrupt_records_empty_on_construct(epics_adapter):
    assert epics_adapter.interrupt_records == {}


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

    cast(Mock, input_record.set).assert_called()


def test_epics_adapter_on_db_load_method(epics_adapter: EpicsAdapter):
    with pytest.raises(NotImplementedError):
        epics_adapter.on_db_load()
