from dataclasses import asdict

from pydantic.v1.dataclasses import dataclass
from pydantic.v1 import parse_obj_as
from tickit.utils.configuration.configurable import as_tagged_union, StrictConfig


@as_tagged_union
@dataclass(config=StrictConfig)
class MyBase:
    pass


@dataclass(config=StrictConfig)
class MyClass(MyBase):
    a: int
    b: str


@dataclass(config=StrictConfig)
class MyOtherClass(MyBase):
    a: int
    c: float


def test_tagged_union_deserializes():
    expected = MyClass(a=1, b="foo")
    expected_serialisation = {"type": "test_configurable.MyClass", "a": 1, "b": "foo"}
    assert asdict(expected) == expected_serialisation
    assert parse_obj_as(MyBase, expected_serialisation) == expected


def test_deserialization_schema():
    assert MyBase.__pydantic_model__.schema() == {
        "$schema": "http://json-schema.org/draft/2020-12/schema#",
        "additionalProperties": False,
        "maxProperties": 1,
        "minProperties": 1,
        "properties": {
            "test_configurable.MyClass": {
                "additionalProperties": False,
                "properties": {"a": {"type": "integer"}, "b": {"type": "string"}},
                "required": ["a", "b"],
                "type": "object",
            },
            "test_configurable.MyOtherClass": {
                "additionalProperties": False,
                "properties": {"a": {"type": "integer"}, "c": {"type": "number"}},
                "required": ["a", "c"],
                "type": "object",
            },
        },
        "type": "object",
    }
