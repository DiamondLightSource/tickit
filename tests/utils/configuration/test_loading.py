from typing import Iterable

import pydantic.v1.dataclasses
import pytest
from mock import Mock, create_autospec, patch
from mock.mock import mock_open

from tickit.core.components.component import ComponentConfig
from tickit.core.typedefs import ComponentID, ComponentPort, PortID
from tickit.utils.configuration.loading import read_configs


@pytest.fixture
def mock_component_config_type() -> Mock:
    return create_autospec(ComponentConfig, instance=False)


@pytest.fixture
def patch_tagged_union_dict(mock_component_config_type) -> Iterable[Mock]:
    with patch.dict(
        "tickit.utils.configuration.loading.is_tagged_union",
        {mock_component_config_type: True},
    ) as mock:
        yield mock


@pydantic.v1.dataclasses.dataclass
class MockConfig(ComponentConfig):
    pass

    def __call__(self):
        return Mock()


@pytest.fixture
def patch_pydantic_deserialize() -> Iterable[Mock]:
    with patch(
        "tickit.utils.configuration.loading.parse_obj_as",
        autospec=True,
    ) as mock:
        mock.return_value = [
            MockConfig(
                name=ComponentID("foo"),
                inputs={PortID("42"): ComponentPort(ComponentID("bar"), PortID("24"))},
            )
        ]
        yield mock


@pytest.fixture
def patch_yaml_library() -> Iterable[Mock]:
    with patch("tickit.utils.configuration.loading.yaml", autospec=True) as mock:
        yield mock


@pytest.fixture
def patch_builtins_open() -> Iterable[Mock]:
    blank_yaml = ""
    with patch(
        "tickit.utils.configuration.loading.open",
        new=mock_open(read_data=blank_yaml),
    ) as mock:
        yield mock


def test_read_configs(
    patch_builtins_open: Mock,
    patch_pydantic_deserialize: Mock,
):
    configs = read_configs("foo/bar.borg")
    assert isinstance(configs[0], MockConfig)
