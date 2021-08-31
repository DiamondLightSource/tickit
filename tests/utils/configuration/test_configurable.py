from dataclasses import dataclass
from typing import List

import apischema
from pytest import fixture

from tickit.utils.configuration.configurable import (
    Config,
    configurable,
    configurable_base,
)


@fixture
def TestBaseConfig():
    @configurable_base
    @dataclass
    class TestBase:
        base_prop: str

    return TestBase


@fixture
def TestBase(TestBaseConfig):
    class TestBase:
        def __init_subclass__(cls) -> None:
            cls = configurable(TestBaseConfig)(cls)

    return TestBase


@fixture
def TestDerived(TestBase):
    class TestDerived(TestBase):
        def __init__(self, derived_field: int) -> None:
            pass

    return TestDerived


@fixture
def OtherTestDerived(TestBase):
    class OtherTestDerived(TestBase):
        def __init__(self, other_derived_field: float) -> None:
            pass

    return OtherTestDerived


def test_serialization_consistency(TestBaseConfig, TestDerived, OtherTestDerived):
    to_serialize: List[TestBaseConfig] = [
        TestDerived.Config("Hello", 42),
        OtherTestDerived.Config("World", 3.14),
    ]
    serialized = apischema.serialize(List[TestBaseConfig], to_serialize)
    deserialized = apischema.deserialize(List[TestBaseConfig], serialized)
    assert to_serialize == deserialized


def test_configurable_adds_config(TestDerived):
    assert isinstance(TestDerived.Config, Config)


def test_config_fields(TestDerived):
    assert {
        "base_prop": str,
        "derived_field": int,
    } == TestDerived.Config.__annotations__


def test_config_inherits(TestDerived, TestBaseConfig):
    assert TestBaseConfig in TestDerived.Config.__bases__


def test_config_configures(TestDerived):
    assert TestDerived == TestDerived.Config.configures()


def test_configurable_kwargs(TestDerived):
    assert {"derived_field": 42} == TestDerived.Config(
        base_prop="Hello", derived_field=42,
    ).kwargs
