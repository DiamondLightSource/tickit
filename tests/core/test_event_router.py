from typing import List, Set

import pytest

from tickit.core.event_router import EventRouter, InverseWiring, Wiring
from tickit.core.typedefs import Changes, DeviceID, Input, IoId, Output, SimTime


@pytest.fixture
def wiring_struct():
    return {
        DeviceID("Out1"): {IoId("Out1>1"): {(DeviceID("Mid1"), IoId("Mid1<1"))}},
        DeviceID("Out2"): {
            IoId("Out2>1"): {
                (DeviceID("In1"), IoId("In1<2")),
                (DeviceID("Mid1"), IoId("Mid1<2")),
            }
        },
        DeviceID("Mid1"): {IoId("Mid1>1"): {(DeviceID("In1"), IoId("In1<1"))}},
    }


@pytest.fixture
def inverse_wiring_struct():
    return {
        DeviceID("Mid1"): {
            IoId("Mid1<1"): (DeviceID("Out1"), IoId("Out1>1")),
            IoId("Mid1<2"): (DeviceID("Out2"), IoId("Out2>1")),
        },
        DeviceID("In1"): {
            IoId("In1<1"): (DeviceID("Mid1"), IoId("Mid1>1")),
            IoId("In1<2"): (DeviceID("Out2"), IoId("Out2>1")),
        },
    }


@pytest.fixture
def wiring(wiring_struct):
    return Wiring(wiring_struct)


@pytest.fixture
def event_router(wiring):
    return EventRouter(wiring)


def test_wiring_unknown_out_dev(wiring_struct):
    wiring = Wiring(wiring_struct)
    assert dict() == wiring["Out3"]


def test_wiring_unknown_out_io(wiring_struct):
    wiring = Wiring(wiring_struct)
    assert set() == wiring["Out1"]["Out1>2"]


def test_wiring_from_inverse_equal(wiring_struct, inverse_wiring_struct):
    assert Wiring(wiring_struct) == Wiring.from_inverse_wiring(inverse_wiring_struct)


def test_inverse_wiring_unknown_in_dev(inverse_wiring_struct):
    inverse_wiring = InverseWiring(inverse_wiring_struct)
    assert dict() == inverse_wiring["In2"]


def test_inverse_wiring_unknown_in_io(inverse_wiring_struct):
    inverse_wiring = InverseWiring(inverse_wiring_struct)
    with pytest.raises(KeyError):
        inverse_wiring["In1"]["In1<3"]


def test_inverse_wiring_from_wiring_equal(inverse_wiring_struct, wiring_struct):
    assert InverseWiring(inverse_wiring_struct) == InverseWiring.from_wiring(
        wiring_struct
    )


def test_event_router_wiring_from_wiring(wiring: Wiring):
    event_router = EventRouter(wiring)
    assert wiring == event_router.wiring


def test_event_router_wiring_from_inverse(wiring: Wiring):
    inverse_wiring = InverseWiring.from_wiring(wiring)
    event_router = EventRouter(inverse_wiring)
    assert wiring == event_router.wiring


def test_event_router_devices(event_router: EventRouter):
    assert {"Out1", "Out2", "Mid1", "In1"} == event_router.devices


def test_event_router_input_devices(event_router: EventRouter):
    assert {"Mid1", "In1"} == event_router.input_devices


def test_event_router_output_devices(event_router: EventRouter):
    assert {"Out1", "Out2", "Mid1"} == event_router.output_devices


def test_event_router_device_tree(event_router: EventRouter):
    assert {
        "Out1": {"Mid1"},
        "Out2": {"Mid1", "In1"},
        "Mid1": {"In1"},
    } == event_router.device_tree


def test_event_router_inverse_device_tree(event_router: EventRouter):
    assert {
        "Out1": set(),
        "Out2": set(),
        "Mid1": {"Out1", "Out2"},
        "In1": {"Mid1", "Out2"},
    } == event_router.inverse_device_tree


@pytest.mark.parametrize(
    ["root", "expected"],
    [
        ("Out1", {"Out1", "Mid1", "In1"}),
        ("Out2", {"Out2", "Mid1", "In1"}),
        ("Mid1", {"Mid1", "In1"}),
        ("In1", {"In1"}),
    ],
)
def test_event_router_dependants(
    event_router: EventRouter, root: DeviceID, expected: Set[DeviceID]
):
    assert expected == event_router.dependants(root)


@pytest.mark.parametrize(
    ["output", "expected"],
    [
        (
            Output(DeviceID("Out1"), SimTime(10), Changes({"Out1>1": 42}), None),
            [Input(DeviceID("Mid1"), SimTime(10), Changes({"Mid1<1": 42}))],
        )
    ],
)
def test_event_router_route(
    event_router: EventRouter, output: Output, expected: List[Input]
):
    assert expected == event_router.route(output)
