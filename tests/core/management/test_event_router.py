from typing import Set

import pytest
from immutables import Map

from tickit.core.components.component import ComponentConfig
from tickit.core.management.event_router import EventRouter, InverseWiring, Wiring
from tickit.core.typedefs import Changes, ComponentID, Input, Output, PortID, SimTime


@pytest.fixture
def wiring_struct():
    return {
        ComponentID("Out1"): {
            PortID("Out1>1"): {(ComponentID("Mid1"), PortID("Mid1<1"))}
        },
        ComponentID("Out2"): {
            PortID("Out2>1"): {
                (ComponentID("In1"), PortID("In1<2")),
                (ComponentID("Mid1"), PortID("Mid1<2")),
            }
        },
        ComponentID("Mid1"): {
            PortID("Mid1>1"): {(ComponentID("In1"), PortID("In1<1"))}
        },
    }


@pytest.fixture
def inverse_wiring_struct():
    return {
        ComponentID("Mid1"): {
            PortID("Mid1<1"): (ComponentID("Out1"), PortID("Out1>1")),
            PortID("Mid1<2"): (ComponentID("Out2"), PortID("Out2>1")),
        },
        ComponentID("In1"): {
            PortID("In1<1"): (ComponentID("Mid1"), PortID("Mid1>1")),
            PortID("In1<2"): (ComponentID("Out2"), PortID("Out2>1")),
        },
    }


@pytest.fixture
def component_configs_list():
    return [
        ComponentConfig(ComponentID("Out1"), dict()),
        ComponentConfig(ComponentID("Out2"), dict()),
        ComponentConfig(
            ComponentID("Mid1"),
            {
                PortID("Mid1<1"): (ComponentID("Out1"), PortID("Out1>1")),
                PortID("Mid1<2"): (ComponentID("Out2"), PortID("Out2>1")),
            },
        ),
        ComponentConfig(
            ComponentID("In1"),
            {
                PortID("In1<1"): (ComponentID("Mid1"), PortID("Mid1>1")),
                PortID("In1<2"): (ComponentID("Out2"), PortID("Out2>1")),
            },
        ),
    ]


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


def test_inverse_wiring_from_component_configs_equal(
    inverse_wiring_struct, component_configs_list
):
    assert InverseWiring(inverse_wiring_struct) == InverseWiring.from_component_configs(
        component_configs_list
    )


def test_event_router_wiring_from_wiring(wiring: Wiring):
    event_router = EventRouter(wiring)
    assert wiring == event_router.wiring


def test_event_router_wiring_from_inverse(wiring: Wiring):
    inverse_wiring = InverseWiring.from_wiring(wiring)
    event_router = EventRouter(inverse_wiring)
    assert wiring == event_router.wiring


def test_event_router_components(event_router: EventRouter):
    assert {"Out1", "Out2", "Mid1", "In1"} == event_router.components


def test_event_router_input_components(event_router: EventRouter):
    assert {"Mid1", "In1"} == event_router.input_components


def test_event_router_output_components(event_router: EventRouter):
    assert {"Out1", "Out2", "Mid1"} == event_router.output_components


def test_event_router_component_tree(event_router: EventRouter):
    assert {
        "Out1": {"Mid1"},
        "Out2": {"Mid1", "In1"},
        "Mid1": {"In1"},
    } == event_router.component_tree


def test_event_router_inverse_component_tree(event_router: EventRouter):
    assert {
        "Out1": set(),
        "Out2": set(),
        "Mid1": {"Out1", "Out2"},
        "In1": {"Mid1", "Out2"},
    } == event_router.inverse_component_tree


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
    event_router: EventRouter, root: ComponentID, expected: Set[ComponentID]
):
    assert expected == event_router.dependants(root)


@pytest.mark.parametrize(
    ["output", "expected"],
    [
        (
            Output(
                ComponentID("Out1"), SimTime(10), Changes(Map({"Out1>1": 42})), None
            ),
            {Input(ComponentID("Mid1"), SimTime(10), Changes(Map({"Mid1<1": 42})))},
        )
    ],
)
def test_event_router_route(
    event_router: EventRouter, output: Output, expected: Set[Input]
):
    assert expected == event_router.route(output)
