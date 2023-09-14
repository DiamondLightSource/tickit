from typing import Dict, Union

from tickit.core.components.component import Component
from tickit.core.management.event_router import InverseWiring, Wiring
from tickit.core.typedefs import ComponentID


class BaseSystemSimulationAdapter:
    """A base for a SystemComponent adapter."""

    _components: Dict[ComponentID, Component]
    _wiring: Union[Wiring, InverseWiring]

    def setup_adapter(
        self,
        components: Dict[ComponentID, Component],
        wiring: Union[Wiring, InverseWiring],
    ) -> None:
        """Provides the components and wiring of a SystemComponent."""
        self._components = components
        self._wiring = wiring
