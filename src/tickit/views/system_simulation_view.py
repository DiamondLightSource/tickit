from typing import Dict, Union

from tickit.core.components.component import Component
from tickit.core.management.event_router import InverseWiring, Wiring
from tickit.core.typedefs import ComponentID


class SystemSimulationView:
    """A view for providing inspection of system simulations.

    This view assumes the role of a device in that Adapters may use it allow direct
    communication and querying of the given system simulation.

    Views must supply interfaces with the system simulation components and wiring in
    the format:

        _components: Dict[ComponentID, Component]
        _wiring: Union[Wiring, InverseWiring]

    Manipulation of the returned information occurs in the adapters for the given view.
    """

    _components: Dict[ComponentID, Component]
    _wiring: Union[Wiring, InverseWiring]

    def __init__(
        self,
        wiring: Union[Wiring, InverseWiring],
        component_list: Dict[ComponentID, Component],
    ) -> None:
        self._components = component_list
        self._wiring = wiring

    def get_component_ids(self) -> list[ComponentID]:
        """Returns a list of all the components within a given system simulation."""
        return list(self._components.keys())

    def get_component(self, id: ComponentID) -> Union[Component, None]:
        """Returns the component with the corresponding ID."""
        return self._components.get(id)

    def get_wiring(self) -> Union[Wiring, InverseWiring]:
        """Returns the wiring from the SystemSimulationComponent scheduler."""
        return self._wiring
