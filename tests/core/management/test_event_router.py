from typing import Dict, Hashable, Mapping, Set

import pytest
from immutables import Map

from tickit.core.components.component import ComponentConfig
from tickit.core.management.event_router import EventRouter, InverseWiring, Wiring
from tickit.core.typedefs import Changes, ComponentID, ComponentPort, PortID


@pytest.fixture
def wiring_struct_4_1():
    return {
        ComponentID("Out1"): {
            PortID("Out1>1"): {ComponentPort(ComponentID("Mid1"), PortID("Mid1<1"))}
        },
        ComponentID("Out2"): {
            PortID("Out2>1"): {
                ComponentPort(ComponentID("In1"), PortID("In1<2")),
                ComponentPort(ComponentID("Mid1"), PortID("Mid1<2")),
            }
        },
        ComponentID("Mid1"): {
            PortID("Mid1>1"): {ComponentPort(ComponentID("In1"), PortID("In1<1"))}
        },
        ComponentID("In1"): {},
        ComponentID("Iso1"): {},
    }


@pytest.fixture
def inverse_wiring_struct_4_1():
    return {
        ComponentID("Iso1"): {},
        ComponentID("Out1"): {},
        ComponentID("Out2"): {},
        ComponentID("Mid1"): {
            PortID("Mid1<1"): ComponentPort(ComponentID("Out1"), PortID("Out1>1")),
            PortID("Mid1<2"): ComponentPort(ComponentID("Out2"), PortID("Out2>1")),
        },
        ComponentID("In1"): {
            PortID("In1<1"): ComponentPort(ComponentID("Mid1"), PortID("Mid1>1")),
            PortID("In1<2"): ComponentPort(ComponentID("Out2"), PortID("Out2>1")),
        },
    }


@pytest.fixture
def component_configs_list_4_1():
    return [
        ComponentConfig(ComponentID("Out1"), dict()),
        ComponentConfig(ComponentID("Out2"), dict()),
        ComponentConfig(
            ComponentID("Mid1"),
            {
                PortID("Mid1<1"): ComponentPort(ComponentID("Out1"), PortID("Out1>1")),
                PortID("Mid1<2"): ComponentPort(ComponentID("Out2"), PortID("Out2>1")),
            },
        ),
        ComponentConfig(
            ComponentID("In1"),
            {
                PortID("In1<1"): ComponentPort(ComponentID("Mid1"), PortID("Mid1>1")),
                PortID("In1<2"): ComponentPort(ComponentID("Out2"), PortID("Out2>1")),
            },
        ),
        ComponentConfig(ComponentID("Iso1"), dict()),
    ]


@pytest.fixture
def component_set_4_1():
    return {"Out1", "Out2", "Mid1", "In1", "Iso1"}


@pytest.fixture
def input_component_set_4_1():
    return {"Mid1", "In1"}


@pytest.fixture
def output_component_set_4_1():
    return {"Out1", "Out2", "Mid1"}


@pytest.fixture
def isolated_component_set_4_1():
    return {"Iso1"}


@pytest.fixture
def wiring(wiring_struct_4_1):
    return Wiring(wiring_struct_4_1)


@pytest.fixture
def event_router(wiring):
    return EventRouter(wiring)


def test_wiring_unknown_out_dev(wiring_struct_4_1):
    wiring = Wiring(wiring_struct_4_1)
    assert dict() == wiring["Out3"]


def test_wiring_unknown_out_io(wiring_struct_4_1):
    wiring = Wiring(wiring_struct_4_1)
    assert set() == wiring["Out1"]["Out1>2"]


def test_inverse_wiring_unknown_in_dev(inverse_wiring_struct_4_1):
    inverse_wiring = InverseWiring(inverse_wiring_struct_4_1)
    assert dict() == inverse_wiring["In2"]


def test_inverse_wiring_unknown_in_io(inverse_wiring_struct_4_1):
    inverse_wiring = InverseWiring(inverse_wiring_struct_4_1)
    with pytest.raises(KeyError):
        inverse_wiring["In1"]["In1<3"]


def test_event_router_component_tree(event_router: EventRouter):
    assert {
        "Iso1": set(),
        "In1": set(),
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
        "Iso1": set(),
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
    ["source", "changes", "expected"],
    [
        (
            ComponentID("Out1"),
            Changes(Map({PortID("Out1>1"): 42})),
            {ComponentID("Mid1"): {PortID("Mid1<1"): 42}},
        )
    ],
)
def test_event_router_route(
    event_router: EventRouter,
    source: ComponentID,
    changes: Mapping[PortID, Hashable],
    expected: Dict[ComponentID, Dict[PortID, object]],
):
    assert expected == event_router.route(source, changes)


# 1 Graph with 1 device (1)


@pytest.fixture
def wiring_struct_1():
    return {
        ComponentID("Iso1"): {},
    }


@pytest.fixture
def inverse_wiring_struct_1():
    return {
        ComponentID("Iso1"): {},
    }


@pytest.fixture
def component_configs_list_1():
    return [
        ComponentConfig(ComponentID("Iso1"), dict()),
    ]


@pytest.fixture
def component_set_1():
    return {"Iso1"}


@pytest.fixture
def input_component_set_1():
    return set()


@pytest.fixture
def output_component_set_1():
    return set()


@pytest.fixture
def isolated_component_set_1():
    return {"Iso1"}


# 2 graphs each with 1 device (1,1)


@pytest.fixture
def wiring_struct_1_1():
    return {
        ComponentID("Iso1"): {},
        ComponentID("Iso2"): {},
    }


@pytest.fixture
def inverse_wiring_struct_1_1():
    return {
        ComponentID("Iso1"): {},
        ComponentID("Iso2"): {},
    }


@pytest.fixture
def component_configs_list_1_1():
    return [
        ComponentConfig(ComponentID("Iso1"), dict()),
        ComponentConfig(ComponentID("Iso2"), dict()),
    ]


@pytest.fixture
def component_set_1_1():
    return {"Iso1", "Iso2"}


@pytest.fixture
def input_component_set_1_1():
    return set()


@pytest.fixture
def output_component_set_1_1():
    return set()


@pytest.fixture
def isolated_component_set_1_1():
    return {"Iso1", "Iso2"}


# 2 graphs each with 2 devices (2,2)


@pytest.fixture
def wiring_struct_2_2():
    return {
        ComponentID("Out1"): {
            PortID("Out1>1"): {ComponentPort(ComponentID("In1"), PortID("In1<1"))}
        },
        ComponentID("In1"): {},
        ComponentID("Out2"): {
            PortID("Out2>1"): {ComponentPort(ComponentID("In2"), PortID("In2<1"))}
        },
        ComponentID("In2"): {},
    }


@pytest.fixture
def inverse_wiring_struct_2_2():
    return {
        ComponentID("Out1"): {},
        ComponentID("Out2"): {},
        ComponentID("In1"): {
            PortID("In1<1"): ComponentPort(ComponentID("Out1"), PortID("Out1>1")),
        },
        ComponentID("In2"): {
            PortID("In2<1"): ComponentPort(ComponentID("Out2"), PortID("Out2>1")),
        },
    }


@pytest.fixture
def component_configs_list_2_2():
    return [
        ComponentConfig(ComponentID("Out1"), dict()),
        ComponentConfig(ComponentID("Out2"), dict()),
        ComponentConfig(
            ComponentID("In1"),
            {
                PortID("In1<1"): ComponentPort(ComponentID("Out1"), PortID("Out1>1")),
            },
        ),
        ComponentConfig(
            ComponentID("In2"),
            {
                PortID("In2<1"): ComponentPort(ComponentID("Out2"), PortID("Out2>1")),
            },
        ),
    ]


@pytest.fixture
def component_set_2_2():
    return {"Out1", "Out2", "In1", "In2"}


@pytest.fixture
def input_component_set_2_2():
    return {"In1", "In2"}


@pytest.fixture
def output_component_set_2_2():
    return {"Out1", "Out2"}


@pytest.fixture
def isolated_component_set_2_2():
    return set()


# 3 graphs, one with 3 devices and two with 1 (3,1,1)


@pytest.fixture
def wiring_struct_3_1_1():
    return {
        ComponentID("Out1"): {
            PortID("Out1>1"): {ComponentPort(ComponentID("Mid1"), PortID("Mid1<1"))}
        },
        ComponentID("Mid1"): {
            PortID("Mid1>1"): {ComponentPort(ComponentID("In1"), PortID("In1<1"))}
        },
        ComponentID("In1"): {},
        ComponentID("Iso1"): {},
        ComponentID("Iso2"): {},
    }


@pytest.fixture
def inverse_wiring_struct_3_1_1():
    return {
        ComponentID("Iso1"): {},
        ComponentID("Iso2"): {},
        ComponentID("Out1"): {},
        ComponentID("Mid1"): {
            PortID("Mid1<1"): ComponentPort(ComponentID("Out1"), PortID("Out1>1")),
        },
        ComponentID("In1"): {
            PortID("In1<1"): ComponentPort(ComponentID("Mid1"), PortID("Mid1>1")),
        },
    }


@pytest.fixture
def component_configs_list_3_1_1():
    return [
        ComponentConfig(ComponentID("Iso1"), dict()),
        ComponentConfig(ComponentID("Iso2"), dict()),
        ComponentConfig(ComponentID("Out1"), dict()),
        ComponentConfig(
            ComponentID("Mid1"),
            {
                PortID("Mid1<1"): ComponentPort(ComponentID("Out1"), PortID("Out1>1")),
            },
        ),
        ComponentConfig(
            ComponentID("In1"),
            {
                PortID("In1<1"): ComponentPort(ComponentID("Mid1"), PortID("Mid1>1")),
            },
        ),
    ]


@pytest.fixture
def component_set_3_1_1():
    return {"Out1", "Mid1", "In1", "Iso1", "Iso2"}


@pytest.fixture
def input_component_set_3_1_1():
    return {"Mid1", "In1"}


@pytest.fixture
def output_component_set_3_1_1():
    return {"Out1", "Mid1"}


@pytest.fixture
def isolated_component_set_3_1_1():
    return {"Iso1", "Iso2"}


# 3 graphs, one with 3 devices and two with 2 (3,2,2)


@pytest.fixture
def wiring_struct_3_2_2():
    return {
        ComponentID("Out1"): {
            PortID("Out1>1"): {ComponentPort(ComponentID("Mid1"), PortID("Mid1<1"))}
        },
        ComponentID("Mid1"): {
            PortID("Mid1>1"): {ComponentPort(ComponentID("In1"), PortID("In1<1"))}
        },
        ComponentID("In1"): {},
        ComponentID("Out2"): {
            PortID("Out2>1"): {ComponentPort(ComponentID("In2"), PortID("In2<1"))}
        },
        ComponentID("In2"): {},
        ComponentID("Out3"): {
            PortID("Out3>1"): {ComponentPort(ComponentID("In3"), PortID("In3<1"))}
        },
        ComponentID("In3"): {},
    }


@pytest.fixture
def inverse_wiring_struct_3_2_2():
    return {
        ComponentID("Out3"): {},
        ComponentID("Out2"): {},
        ComponentID("Out1"): {},
        ComponentID("Mid1"): {
            PortID("Mid1<1"): ComponentPort(ComponentID("Out1"), PortID("Out1>1")),
        },
        ComponentID("In1"): {
            PortID("In1<1"): ComponentPort(ComponentID("Mid1"), PortID("Mid1>1")),
        },
        ComponentID("In2"): {
            PortID("In2<1"): ComponentPort(ComponentID("Out2"), PortID("Out2>1")),
        },
        ComponentID("In3"): {
            PortID("In3<1"): ComponentPort(ComponentID("Out3"), PortID("Out3>1")),
        },
    }


@pytest.fixture
def component_configs_list_3_2_2():
    return [
        ComponentConfig(ComponentID("Out3"), dict()),
        ComponentConfig(ComponentID("Out2"), dict()),
        ComponentConfig(ComponentID("Out1"), dict()),
        ComponentConfig(
            ComponentID("Mid1"),
            {
                PortID("Mid1<1"): ComponentPort(ComponentID("Out1"), PortID("Out1>1")),
            },
        ),
        ComponentConfig(
            ComponentID("In1"),
            {
                PortID("In1<1"): ComponentPort(ComponentID("Mid1"), PortID("Mid1>1")),
            },
        ),
        ComponentConfig(
            ComponentID("In2"),
            {
                PortID("In2<1"): ComponentPort(ComponentID("Out2"), PortID("Out2>1")),
            },
        ),
        ComponentConfig(
            ComponentID("In3"),
            {
                PortID("In3<1"): ComponentPort(ComponentID("Out3"), PortID("Out3>1")),
            },
        ),
    ]


@pytest.fixture
def component_set_3_2_2():
    return {"Out1", "Mid1", "In1", "Out2", "In2", "Out3", "In3"}


@pytest.fixture
def input_component_set_3_2_2():
    return {"Mid1", "In1", "In2", "In3"}


@pytest.fixture
def output_component_set_3_2_2():
    return {"Out1", "Mid1", "Out2", "Out3"}


@pytest.fixture
def isolated_component_set_3_2_2():
    return set()


@pytest.mark.parametrize(
    "wiring_struct, inverse_wiring_struct",
    [
        ("wiring_struct_1", "inverse_wiring_struct_1"),
        ("wiring_struct_1_1", "inverse_wiring_struct_1_1"),
        ("wiring_struct_2_2", "inverse_wiring_struct_2_2"),
        ("wiring_struct_3_1_1", "inverse_wiring_struct_3_1_1"),
        ("wiring_struct_3_2_2", "inverse_wiring_struct_3_2_2"),
        ("wiring_struct_4_1", "inverse_wiring_struct_4_1"),
    ],
)
def test_wiring_from_inverse_equal(wiring_struct, inverse_wiring_struct, request):
    assert Wiring(request.getfixturevalue(wiring_struct)) == Wiring.from_inverse_wiring(
        request.getfixturevalue(inverse_wiring_struct)
    )


@pytest.mark.parametrize(
    "wiring_struct, inverse_wiring_struct",
    [
        ("wiring_struct_1", "inverse_wiring_struct_1"),
        ("wiring_struct_1_1", "inverse_wiring_struct_1_1"),
        ("wiring_struct_2_2", "inverse_wiring_struct_2_2"),
        ("wiring_struct_3_1_1", "inverse_wiring_struct_3_1_1"),
        ("wiring_struct_3_2_2", "inverse_wiring_struct_3_2_2"),
        ("wiring_struct_4_1", "inverse_wiring_struct_4_1"),
    ],
)
def test_inverse_wiring_from_wiring_equal(
    wiring_struct, inverse_wiring_struct, request
):
    assert InverseWiring(
        request.getfixturevalue(inverse_wiring_struct)
    ) == InverseWiring.from_wiring(request.getfixturevalue(wiring_struct))


@pytest.mark.parametrize(
    "inverse_wiring_struct, component_configs_list",
    [
        ("inverse_wiring_struct_1", "component_configs_list_1"),
        ("inverse_wiring_struct_1_1", "component_configs_list_1_1"),
        ("inverse_wiring_struct_2_2", "component_configs_list_2_2"),
        ("inverse_wiring_struct_3_1_1", "component_configs_list_3_1_1"),
        ("inverse_wiring_struct_3_2_2", "component_configs_list_3_2_2"),
        ("inverse_wiring_struct_4_1", "component_configs_list_4_1"),
    ],
)
def test_inverse_wiring_from_component_configs_equal(
    inverse_wiring_struct, component_configs_list, request
):
    assert InverseWiring(
        request.getfixturevalue(inverse_wiring_struct)
    ) == InverseWiring.from_component_configs(
        request.getfixturevalue(component_configs_list)
    )


@pytest.mark.parametrize(
    "wiring_struct",
    [
        ("wiring_struct_1"),
        ("wiring_struct_1_1"),
        ("wiring_struct_2_2"),
        ("wiring_struct_3_1_1"),
        ("wiring_struct_3_2_2"),
        ("wiring_struct_4_1"),
    ],
)
def test_event_router_wiring_from_wiring(wiring_struct, request):
    wiring = Wiring(request.getfixturevalue(wiring_struct))
    event_router = EventRouter(wiring)
    assert wiring == event_router.wiring


@pytest.mark.parametrize(
    "wiring_struct",
    [
        ("wiring_struct_1"),
        ("wiring_struct_1_1"),
        ("wiring_struct_2_2"),
        ("wiring_struct_3_1_1"),
        ("wiring_struct_3_2_2"),
        ("wiring_struct_4_1"),
    ],
)
def test_event_router_wiring_from_inverse(wiring_struct, request):
    wiring = Wiring(request.getfixturevalue(wiring_struct))
    inverse_wiring = InverseWiring.from_wiring(wiring)
    event_router = EventRouter(inverse_wiring)
    assert wiring == event_router.wiring


@pytest.mark.parametrize(
    "wiring_struct, component_set",
    [
        ("wiring_struct_1", "component_set_1"),
        ("wiring_struct_1_1", "component_set_1_1"),
        ("wiring_struct_2_2", "component_set_2_2"),
        ("wiring_struct_3_1_1", "component_set_3_1_1"),
        ("wiring_struct_3_2_2", "component_set_3_2_2"),
        ("wiring_struct_4_1", "component_set_4_1"),
    ],
)
def test_event_router_components(wiring_struct, component_set, request):
    event_router = EventRouter(Wiring(request.getfixturevalue(wiring_struct)))
    assert request.getfixturevalue(component_set) == event_router.components


@pytest.mark.parametrize(
    "wiring_struct, input_component_set",
    [
        ("wiring_struct_1", "input_component_set_1"),
        ("wiring_struct_1_1", "input_component_set_1_1"),
        ("wiring_struct_2_2", "input_component_set_2_2"),
        ("wiring_struct_3_1_1", "input_component_set_3_1_1"),
        ("wiring_struct_3_2_2", "input_component_set_3_2_2"),
        ("wiring_struct_4_1", "input_component_set_4_1"),
    ],
)
def test_event_router_input_components(wiring_struct, input_component_set, request):
    event_router = EventRouter(Wiring(request.getfixturevalue(wiring_struct)))
    assert request.getfixturevalue(input_component_set) == event_router.input_components


@pytest.mark.parametrize(
    "wiring_struct, output_component_set",
    [
        ("wiring_struct_1", "output_component_set_1"),
        ("wiring_struct_1_1", "output_component_set_1_1"),
        ("wiring_struct_2_2", "output_component_set_2_2"),
        ("wiring_struct_3_1_1", "output_component_set_3_1_1"),
        ("wiring_struct_3_2_2", "output_component_set_3_2_2"),
        ("wiring_struct_4_1", "output_component_set_4_1"),
    ],
)
def test_event_router_output_components(wiring_struct, output_component_set, request):
    event_router = EventRouter(Wiring(request.getfixturevalue(wiring_struct)))
    assert (
        request.getfixturevalue(output_component_set) == event_router.output_components
    )


@pytest.mark.parametrize(
    "wiring_struct, isolated_component_set",
    [
        ("wiring_struct_1", "isolated_component_set_1"),
        ("wiring_struct_1_1", "isolated_component_set_1_1"),
        ("wiring_struct_2_2", "isolated_component_set_2_2"),
        ("wiring_struct_3_1_1", "isolated_component_set_3_1_1"),
        ("wiring_struct_3_2_2", "isolated_component_set_3_2_2"),
        ("wiring_struct_4_1", "isolated_component_set_4_1"),
    ],
)
def test_event_router_isolated_components(
    wiring_struct, isolated_component_set, request
):
    event_router = EventRouter(Wiring(request.getfixturevalue(wiring_struct)))
    assert (
        request.getfixturevalue(isolated_component_set)
        == event_router.isolated_components
    )
