from typing import Dict

import pytest
from mock import MagicMock, Mock, mock_open, patch

from tickit.adapters.epics import EpicsAdapter
from tickit.adapters.io.epics_io import EpicsIo
from tickit.core.adapter import AdapterContainer, RaiseInterrupt


@pytest.fixture
def epics_adapter() -> EpicsAdapter:
    return EpicsAdapter()


@pytest.fixture
def epics_io() -> EpicsIo:
    return EpicsIo("ioc_name", db_file="db_file")


@pytest.fixture
def epics_io_no_db_file() -> EpicsIo:
    return EpicsIo("ioc_name")


def record_db_file_contents() -> Dict[str, bytes]:
    return {
        "data": b"""record(ao, "$(device):GAIN") {
        field(DTYP, "Hy8001")
        field(OMSL, "supervisory")
        field(OUT, "#C1 S0 @")
        field(DESC, "Gain value")
        field(EGU, "A")
        }""",
        "expected": b"""record(ao, "$(device):GAIN") {
        field(OMSL, "supervisory")
        field(OUT, "#C1 S0 @")
        field(DESC, "Gain value")
        field(EGU, "A")
        }""",
    }


def filter1_db_file_contents() -> Dict[str, bytes]:
    return {
        "data": b"""record(bo, "$(device):FILTER") {
        field(DTYP, "$(DTYP)")
        field(SCAN, "Passive")
        field(ZNAM, "Out")
        field(ONAM, "In")
        field(VAL, "0")
        field(OMSL, "closed_loop")
        }""",
        "expected": b"""record(bo, "$(device):FILTER") {
        field(SCAN, "Passive")
        field(ZNAM, "Out")
        field(ONAM, "In")
        field(VAL, "0")
        field(OMSL, "closed_loop")
        }""",
    }


@pytest.mark.parametrize(
    "test_params",
    [
        pytest.param(record_db_file_contents(), id="record.db file contents"),
        pytest.param(filter1_db_file_contents(), id="filter.db file contents"),
    ],
)
def test_epics_adapter_load_records_without_DTYP_fields_method(
    epics_io: EpicsIo,
    test_params: Dict[str, bytes],
):
    data = test_params["data"]
    with patch("builtins.open", mock_open(read_data=data)):
        with patch("os.unlink") as mock_unlink:
            epics_io.load_records_without_DTYP_fields()
            unlink_args = mock_unlink.call_args.args

    out_filename = unlink_args[0]
    with open(out_filename, "rb") as file:
        written_data = file.read()

    assert str(written_data).strip() == str(test_params["expected"]).strip()


@pytest.fixture
def mock_raise_interrupt():
    async def raise_interrupt():
        return False

    return Mock(raise_interrupt)


@pytest.mark.asyncio
async def test_db_file_not_specified(
    epics_adapter: EpicsAdapter,
    epics_io_no_db_file: EpicsIo,
    mock_raise_interrupt: RaiseInterrupt,
):
    epics_container = AdapterContainer(epics_adapter, epics_io_no_db_file)

    epics_container.adapter.on_db_load = MagicMock()  # type: ignore
    epics_container.io.load_records_without_DTYP_fields = MagicMock()  # type: ignore

    await epics_container.run_forever(mock_raise_interrupt)

    epics_container.io.load_records_without_DTYP_fields.assert_not_called()  # type: ignore # noqa: E501,


@pytest.mark.asyncio
async def test_db_load_called_if_file_specified(
    epics_adapter: EpicsAdapter,
    epics_io: EpicsIo,
    mock_raise_interrupt: RaiseInterrupt,
):
    epics_container = AdapterContainer(epics_adapter, epics_io)

    epics_container.adapter.on_db_load = MagicMock()  # type: ignore
    epics_container.io.load_records_without_DTYP_fields = MagicMock()  # type: ignore

    await epics_container.run_forever(mock_raise_interrupt)

    epics_container.io.load_records_without_DTYP_fields.assert_called_once()  # type: ignore # noqa: E501,
