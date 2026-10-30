from tickit.core.components.component import Component
from tickit.core.management.event_router import InverseWiring, Wiring
from tickit.core.typedefs import ComponentID


class BaseSystemSimulationAdapter:
    """A base for a SystemComponent adapter."""

    _components: dict[ComponentID, Component]
    _wiring: Wiring | InverseWiring

    def setup_adapter(
        self,
        components: dict[ComponentID, Component],
        wiring: Wiring | InverseWiring,
    ) -> None:
        """Provides the components and wiring of a SystemComponent."""
        self._components = components
        self._wiring = wiring
