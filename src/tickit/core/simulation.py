import asyncio
import logging
from typing import Dict, List, Optional, Set

from tickit.core.components.component import Component
from tickit.core.management.event_router import InverseWiring
from tickit.core.management.schedulers.master import MasterScheduler
from tickit.core.state_interfaces.state_interface import get_interface
from tickit.core.typedefs import ComponentID
from tickit.utils.configuration.loading import read_configs

LOGGER = logging.getLogger(__name__)


class TickitSimulation:
    """A Simulation runner/worker."""

    _backend: str

    _scheduler: MasterScheduler
    _components: Dict[ComponentID, Component]

    _tasks: List[asyncio.Task] = []

    _include_schedulers: bool
    _include_components: bool
    _components_to_run: Set[ComponentID]

    def __init__(
        self,
        config_path: str,
        backend: str = "internal",
        include_schedulers: bool = True,
        include_components: bool = True,
        components_to_run: Optional[Set[ComponentID]] = None,
    ) -> None:
        """Sets up the master scheduler and the components for a simulation.

        A config file is loaded, retrieving the relevant components. The wiring of
        these components is generated and used to make the master scheduler for the
        simulation.

        By default the scheduler is included

        """
        self._backend = backend
        configs = read_configs(config_path)
        inverse_wiring = InverseWiring.from_component_configs(configs)

        self._scheduler = MasterScheduler(inverse_wiring, *get_interface(backend))
        self._components = {config.name: config() for config in configs}

        self._include_schedulers = include_schedulers
        self._include_components = include_components
        self._components_to_run = components_to_run or set(self._components.keys())

    def _start_scheduler_tasks(self) -> None:
        self._tasks.append(asyncio.create_task(self._scheduler.run_forever()))

    def _start_component_tasks(self) -> None:
        for component_id in self._components_to_run:
            try:
                component = self._components[component_id]
            except KeyError:
                LOGGER.exception(f" Component {component_id} not found")
                raise

            self._tasks.append(
                asyncio.create_task(
                    component.run_forever(*get_interface(self._backend))
                )
            )

    async def run(self) -> None:
        """Awaits the scheduler and/or component tasks indefinitely."""
        if self._include_schedulers:
            self._start_scheduler_tasks()
        if self._include_components:
            self._start_component_tasks()
        await asyncio.wait(self._tasks)
