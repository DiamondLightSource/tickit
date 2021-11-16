from dataclasses import dataclass

from apischema import deserialize
from apischema.json_schema import deserialization_schema

from tickit.utils.configuration.configurable import as_tagged_union


@as_tagged_union
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
    actual = deserialize(MyBase, {"test_configurable.MyClass": {"a": 1, "b": "foo"}})
    assert actual == expected


def test_deserialization_schema():
    assert deserialization_schema(MyBase) == {
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
