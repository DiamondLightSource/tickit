import pytest

from tickit.devices.eiger.filewriter.filewriter_status import FileWriterStatus

# # # # # Eiger FileWriterStatus Tests # # # # #


@pytest.fixture
def filewriter_status() -> FileWriterStatus:
    return FileWriterStatus()


def test_eiger_filewriter_status_constructor():
    FileWriterStatus()


def test_eiger_status_getitem(filewriter_status):
    assert "ready" == filewriter_status["state"]["value"]
