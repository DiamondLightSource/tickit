from dataclasses import is_dataclass
from typing import Optional

from tickit.core.typedefs import (
    Changes,
    ComponentException,
    ComponentID,
    Input,
    Interrupt,
    Output,
    SimTime,
    StopComponent,
)


def test_input_is_dataclass():
    assert is_dataclass(Input)


def test_input_has_target():
    assert ComponentID == Input.__annotations__["target"]


def test_input_has_time():
    assert SimTime == Input.__annotations__["time"]


def test_input_has_changes():
    assert Changes == Input.__annotations__["changes"]


def test_stop_component_is_dataclass():
    assert is_dataclass(StopComponent)


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


def test_interrupt_is_dataclass():
    assert is_dataclass(Interrupt)


def test_interrupt_has_source():
    assert ComponentID == Interrupt.__annotations__["source"]


def test_component_exception_is_dataclass():
    assert is_dataclass(ComponentException)


def test_component_exception_has_source():
    assert ComponentID == ComponentException.__annotations__["source"]


def test_component_exception_has_error():
    assert Exception == ComponentException.__annotations__["error"]


def test_component_exception_has_traceback():
    assert str == ComponentException.__annotations__["traceback"]
