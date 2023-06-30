import asyncio
from dataclasses import field
from typing import Dict, List

from tickit.core.components.component import Component
from tickit.core.management.event_router import InverseWiring
from tickit.core.management.schedulers.master import MasterScheduler
from tickit.core.runner import run_all
from tickit.core.state_interfaces.state_interface import get_interface
from tickit.core.typedefs import ComponentID
from tickit.utils.configuration.loading import read_configs


class TickitSimulation:
    """A Simulation runner/worker."""

    _scheduler: MasterScheduler
    _components: Dict[ComponentID, Component]

    _tasks: List[asyncio.Task] = field(default_factory=list)

    backend: str

    def __init__(self, config_path: str, backend: str = "internal") -> None:
        self.backend = backend
        configs = read_configs(config_path)
        inverse_wiring = InverseWiring.from_component_configs(configs)

        self._scheduler = MasterScheduler(inverse_wiring, *get_interface(backend))
        self._components = {config.name: config() for config in configs}

    async def run_forever(self) -> None:
        """Sets the scheduler and components to run continuously."""
        self._tasks = run_all(
            [
                component.run_forever(*get_interface(self.backend))
                for component in self._components.values()
            ]
            + [self._scheduler.run_forever()]
        )
        await asyncio.wait(self._tasks)
