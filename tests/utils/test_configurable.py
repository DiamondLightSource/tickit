from dataclasses import asdict

from tickit.utils.compat.pydantic_compat import parse_obj_as, pydantic_dataclass
from tickit.utils.configuration.configurable import as_tagged_union


@as_tagged_union
@pydantic_dataclass
class MyBase:
    pass


@pydantic_dataclass
class MyClass(MyBase):
    a: int
    b: str


@pydantic_dataclass
class MyOtherClass(MyBase):
    a: int
    b: float


@as_tagged_union
@pydantic_dataclass
class Superclass:
    pass


@pydantic_dataclass
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
