from dataclasses import asdict

import pydantic.v1.dataclasses
from pydantic.v1 import parse_obj_as

from tickit.utils.configuration.tagged_union import as_tagged_union


@as_tagged_union
@pydantic.v1.dataclasses.dataclass
class MyBase:
    pass


@pydantic.v1.dataclasses.dataclass
class MyClass(MyBase):
    a: int
    b: str


@pydantic.v1.dataclasses.dataclass
class MyOtherClass(MyBase):
    a: int
    b: float


@as_tagged_union
@pydantic.v1.dataclasses.dataclass
class Superclass:
    pass


@pydantic.v1.dataclasses.dataclass
class LoneSubclass(Superclass):
    pass


def test_tagged_union_deserializes():
    expected = MyClass(a=1, b="foo")
    expected_serialisation = {"type": "test_configurable.MyClass", "a": 1, "b": "foo"}
    assert asdict(expected) == expected_serialisation
    assert parse_obj_as(MyBase, expected_serialisation) == expected


def test_tagged_union_deserializes_not_as_first_defined_subclass():
    expected = MyOtherClass(a=1, b=8.0)
    expected_serialisation = {"type": "test_configurable.MyOtherClass", "a": 1, "b": 8}
    assert asdict(expected) == expected_serialisation
    assert parse_obj_as(MyBase, expected_serialisation) == expected
    # Compatible with being deserialised as MyClass other than the discriminator
    string_serialised = {"type": "test_configurable.MyOtherClass", "a": 1, "b": "8.0"}
    assert parse_obj_as(MyBase, string_serialised) == expected


def test_single_extending_type_deserialises():
    # Python runtime converts Union[A] -> A, ensures special handling is not broken.
    expected = LoneSubclass()
    expected_serialisation = {"type": "test_configurable.LoneSubclass"}
    assert asdict(expected) == expected_serialisation
    assert parse_obj_as(Superclass, expected_serialisation) == expected
