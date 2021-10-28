import pytest

from tickit.devices.eiger.monitor.monitor_status import MonitorStatus

# # # # # Eiger MonitorStatus Tests # # # # #


@pytest.fixture
def monitor_status() -> MonitorStatus:
    return MonitorStatus()


def test_eiger_monitor_status_constructor():
    MonitorStatus()


def test_eiger_monitor_status_getitem(monitor_status):
    assert [] == monitor_status["error"]["value"]
