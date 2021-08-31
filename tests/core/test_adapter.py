from dataclasses import is_dataclass

import pytest

from tickit.core.adapter import (
    AdapterConfig,
    ConfigurableAdapter,
    ConfigurableServer,
    ServerConfig,
)
from tickit.utils.configuration.configurable import Config


def test_adapter_config_is_dataclass():
    assert is_dataclass(AdapterConfig)


def test_adapter_config_is_config():
    isinstance(AdapterConfig, Config)


def test_adapter_config_configures_raises_not_implemented():
    with pytest.raises(NotImplementedError):
        AdapterConfig.configures()


def test_adapter_config_kwargs_raises_not_implemented():
    adapter_config = AdapterConfig()
    with pytest.raises(NotImplementedError):
        adapter_config.kwargs


def test_inherit_configurable_adapter_makes_configurable():
    assert isinstance(type("Adapter", (ConfigurableAdapter,), dict()).Config, Config)


def test_server_config_is_dataclass():
    assert is_dataclass(ServerConfig)


def test_server_config_is_config():
    assert isinstance(ServerConfig, Config)


def test_server_config_configure_raises_not_implemented():
    with pytest.raises(NotImplementedError):
        ServerConfig.configures()


def test_server_config_kwargs_raises_not_implemented():
    server_config = ServerConfig()
    with pytest.raises(NotImplementedError):
        server_config.kwargs


def test_inherit_configurable_server_makes_configurable():
    assert isinstance(type("Server", (ConfigurableServer,), dict()).Config, Config)
