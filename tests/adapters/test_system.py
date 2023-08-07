from typing import Dict

import pytest
from mock import create_autospec

from tickit.adapters.system import BaseSystemSimulationAdapter
from tickit.core.components.component import Component
from tickit.core.management.event_router import Wiring
from tickit.core.typedefs import ComponentID


@pytest.fixture
def mock_components() -> Dict[ComponentID, Component]:
    cpt: Component = create_autospec(Component, instance=True)
    return {ComponentID("mock_cpt"): cpt}


@pytest.fixture
def mock_wiring() -> Wiring:
    wiring: Wiring = create_autospec(Wiring, instance=True)
    return wiring


def test_base_has_components_and_wiring(mock_components, mock_wiring):
    adapter = BaseSystemSimulationAdapter()
    adapter.setup_adapter(mock_components, mock_wiring)

    assert adapter._components is not None
    for key, value in adapter._components.items():
        assert isinstance(key, str)
        assert isinstance(value, Component)

    assert adapter._wiring is not None
    assert isinstance(adapter._wiring, Wiring)
