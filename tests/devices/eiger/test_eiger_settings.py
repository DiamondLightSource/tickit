import pytest

from tickit.devices.eiger.eiger_settings import EigerSettings, KA_Energy

# # # # # EigerStatus Tests # # # # #


@pytest.fixture
def eiger_settings() -> EigerSettings:
    return EigerSettings()


def test_eiger_settings_constructor():
    EigerSettings()


def test_eiger_settings_getitem(eiger_settings):
    value = eiger_settings["count_time"]["value"]

    assert 0.1 == value


def test_eiger_settings_get_element(eiger_settings):
    assert "Co" == eiger_settings.element


def test_eiger_settings_set_element(eiger_settings):
    eiger_settings["element"] = "Li"

    assert "Li" == eiger_settings.element
    assert KA_Energy["Li"].value == eiger_settings.photon_energy
