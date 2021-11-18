import pytest

from tickit.devices.eiger.filewriter.filewriter_config import FileWriterConfig

# # # # # Eiger FileWriterConfig Tests # # # # #


@pytest.fixture
def filewriter_config() -> FileWriterConfig:
    return FileWriterConfig()


def test_eiger_filewriter_config_constructor():
    FileWriterConfig()


def test_eiger_filewriter_config_getitem(filewriter_config):
    assert "enabled" == filewriter_config["mode"]["value"]
