import pytest

from tickit.devices.eiger.monitor.monitor_config import MonitorConfig

# # # # # Eiger MonitorConfig Tests # # # # #


@pytest.fixture
def monitor_config() -> MonitorConfig:
    return MonitorConfig()


def test_eiger_monitor_config_constructor():
    MonitorConfig()


def test_eiger_monitor_config_getitem(monitor_config):
    assert "enabled" == monitor_config["mode"]["value"]
