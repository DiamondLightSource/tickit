from dataclasses import asdict, dataclass
from typing import Any, cast

from tickit.utils.configuration.tagged_union import as_tagged_union


@as_tagged_union
@dataclass
class MyBase:
    pass


@dataclass
class MyClass(MyBase):
    a: int
    b: str


@dataclass
class MyOtherClass(MyBase):
    a: int
    b: float


@as_tagged_union
@dataclass
class Superclass:
    pass


@dataclass
class LoneSubclass(Superclass):
    pass


def test_tagged_union_deserializes():
    expected = MyClass(a=1, b="foo")
    expected_serialisation = {"type": "test_configurable.MyClass", "a": 1, "b": "foo"}
    assert asdict(expected) == expected_serialisation
    assert cast(Any, MyBase)._validate(expected_serialisation) == expected


def test_tagged_union_deserializes_not_as_first_defined_subclass():
    expected = MyOtherClass(a=1, b=8.0)
    expected_serialisation = {"type": "test_configurable.MyOtherClass", "a": 1, "b": 8}
    assert asdict(expected) == expected_serialisation
    assert cast(Any, MyBase)._validate(expected_serialisation) == expected
    # Compatible with being deserialised as MyClass other than the discriminator
    string_serialised = {"type": "test_configurable.MyOtherClass", "a": 1, "b": "8.0"}
    assert cast(Any, MyBase)._validate(string_serialised) == expected


def test_single_extending_type_deserialises():
    # Python runtime converts Union[A] -> A, ensures special handling is not broken.
    expected = LoneSubclass()
    expected_serialisation = {"type": "test_configurable.LoneSubclass"}
    assert asdict(expected) == expected_serialisation
    assert cast(Any, Superclass)._validate(expected_serialisation) == expected
