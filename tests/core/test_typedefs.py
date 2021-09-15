from dataclasses import is_dataclass
from typing import Optional

from tickit.core.typedefs import Changes, ComponentID, Input, Output, SimTime


def test_input_is_dataclass():
    assert is_dataclass(Input)


def test_input_has_target():
    assert ComponentID == Input.__annotations__["target"]


def test_input_has_time():
    assert SimTime == Input.__annotations__["time"]


def test_input_has_changes():
    assert Changes == Input.__annotations__["changes"]


def test_output_is_dataclass():
    assert is_dataclass(Output)


def test_output_has_source():
    assert ComponentID == Output.__annotations__["source"]


def test_output_has_time():
    assert SimTime == Output.__annotations__["time"]


def test_output_has_changes():
    assert Changes == Output.__annotations__["changes"]


def test_output_has_call_in():
    assert Optional[SimTime] == Output.__annotations__["call_at"]
