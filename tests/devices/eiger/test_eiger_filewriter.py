import pytest

from tickit.devices.eiger.filewriter.eiger_filewriter import EigerFileWriter


@pytest.fixture
def filewriter() -> EigerFileWriter:
    return EigerFileWriter()


def test_eiger_filewriter_constructor():
    EigerFileWriter()
