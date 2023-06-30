from typing import Dict, Union
from tickit.core.components.component import Component
from tickit.core.management.event_router import InverseWiring, Wiring
from tickit.core.typedefs import ComponentID


class SystemSimulationView:
    """A view for providing introspection to system simulations.

    This acts like a device for an adapter to communicate with.

    Keep this at the cpt layer, all the device nonsense done with specific adapters
    for views.
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

    def set_wiring(self, wiring: Wiring) -> None:
        """Alter the graph wiring mid simulation.

        - Pause simulation,
        - Cache the states (do we actually want this?),
        - Apply new wiring,
        - match any device that exists in both and apply cached values
        - resume with new tick.

        """
        ...
