from types import new_class
from typing import Type

from _pytest.fixtures import fixture

from tickit.utils.singleton import Singleton


@fixture
def TestSingleton() -> Type:
    return new_class("TestSingleton", tuple(), {"metaclass": Singleton})


@fixture
def OtherSingleton() -> Type:
    return new_class("OtherSingleton", tuple(), {"metaclass": Singleton})


def test_call_creates(TestSingleton):
    assert isinstance(TestSingleton(), object)


def subsequent_call_creates_same(TestSingleton):
    original = TestSingleton()
    assert original == TestSingleton()


def derived_unequal(TestSingleton, OtherSigleton):
    assert TestSingleton() != OtherSigleton()
