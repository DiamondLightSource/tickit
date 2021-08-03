from dataclasses import is_dataclass
from typing import Callable, Hashable, Optional

from tickit.core.typedefs import (
    Changes,
    DeviceID,
    Input,
    IoId,
    Output,
    Port,
    SimTime,
    Wakeup,
)


def test_port_is_dataclass():
    assert is_dataclass(Port)


def test_port_has_device():
    assert DeviceID == Port.__annotations__["device"]


def test_port_has_key():
    assert IoId == Port.__annotations__["key"]


def test_port_is_hashable():
    assert isinstance(Port, Hashable)


def test_port_hashes_as_tuple():
    port = Port(DeviceID("Test"), IoId("Test"))
    assert ("Test", "Test").__hash__() == port.__hash__()


def test_input_is_dataclass():
    assert is_dataclass(Input)


def test_input_has_target():
    assert DeviceID == Input.__annotations__["target"]


def test_input_has_time():
    assert SimTime == Input.__annotations__["time"]


def test_input_has_changes():
    assert Changes == Input.__annotations__["changes"]


def test_output_is_dataclass():
    assert is_dataclass(Output)


def test_output_has_source():
    assert DeviceID == Output.__annotations__["source"]


def test_output_has_time():
    assert Optional[SimTime] == Output.__annotations__["time"]


def test_output_has_changes():
    assert Changes == Output.__annotations__["changes"]


def test_output_has_call_in():
    assert Optional[SimTime] == Output.__annotations__["call_in"]


def test_wakeup_is_dataclass():
    assert is_dataclass(Wakeup)


def test_wakeup_has_device():
    assert DeviceID == Wakeup.__annotations__["device"]


def test_wakeup_has_when():
    assert SimTime == Wakeup.__annotations__["when"]


def test_wakeup_implements_lt():
    assert isinstance(Wakeup.__lt__, Callable)


def test_wakeup_lt_correct_less():
    assert Wakeup(DeviceID("TestDevice"), SimTime(10)) < Wakeup(
        DeviceID("OtherTestDevice"), SimTime(20)
    )


def test_wakeup_lt_correct_greater():
    assert not Wakeup(DeviceID("TestDevice"), SimTime(20)) < Wakeup(
        DeviceID("OtherTestDevice"), SimTime(10)
    )
