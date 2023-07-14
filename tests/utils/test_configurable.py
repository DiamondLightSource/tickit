from dataclasses import asdict

from pydantic.v1 import parse_obj_as
from pydantic.v1.dataclasses import dataclass

from tickit.utils.configuration.configurable import as_tagged_union


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
    c: float


def test_tagged_union_deserializes():
    expected = MyClass(a=1, b="foo")
    expected_serialisation = {"type": "test_configurable.MyClass", "a": 1, "b": "foo"}
    assert asdict(expected) == expected_serialisation
    assert parse_obj_as(MyBase, expected_serialisation) == expected

