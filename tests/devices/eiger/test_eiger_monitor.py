import pytest

from tickit.devices.eiger.monitor.eiger_monitor import EigerMonitor


@pytest.fixture
def filewriter() -> EigerMonitor:
    return EigerMonitor()


def test_eiger_monitor_constructor():
    EigerMonitor()
