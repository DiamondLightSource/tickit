from tickit.core.simulation import TickitSimulationBuilder
from tickit.core.typedefs import ComponentID


def test_builder_scheduler_and_components_included_by_default() -> None:
    tickit_simulation_builder = TickitSimulationBuilder("tests/core/sim.yaml")

    assert tickit_simulation_builder._include_components is True
    assert tickit_simulation_builder._include_schedulers is True


def test__builder_backend_internal_by_default() -> None:
    tickit_simulation_builder = TickitSimulationBuilder("tests/core/sim.yaml")

    assert tickit_simulation_builder._backend == "internal"


def test_builder_choose_components_to_run() -> None:
    tickit_simulation_builder = TickitSimulationBuilder(
        "tests/core/sim.yaml",
        components_to_run={ComponentID("source")},
    )
    assert tickit_simulation_builder._components_to_run == {"source"}


def test_builder_default_includes_all_components_in_simulation() -> None:
    tickit_simulation_builder = TickitSimulationBuilder("tests/core/sim.yaml")
    assert tickit_simulation_builder._components_to_run == set()

    tickit_simulation = tickit_simulation_builder.build()
    assert set(tickit_simulation._components.keys()) == {  # type: ignore
        "source",
        "sink",
    }


def test_choosing_all_components_equivalent_to_choosing_none() -> None:
    tickit_simulation_builder = TickitSimulationBuilder(
        "tests/core/sim.yaml",
        components_to_run={ComponentID("source"), ComponentID("sink")},
    )
    tickit_simulation = tickit_simulation_builder.build()

    tickit_simulation_builder_2 = TickitSimulationBuilder("tests/core/sim.yaml")
    tickit_simulation_2 = tickit_simulation_builder_2.build()

    assert (
        tickit_simulation._components.keys()  # type: ignore
        == tickit_simulation_2._components.keys()  # type: ignore
    )
