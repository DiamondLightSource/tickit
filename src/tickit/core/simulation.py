import asyncio
import logging
from typing import Dict, Iterable, Optional, Set

from tickit.core.components.component import Component
from tickit.core.management.event_router import InverseWiring
from tickit.core.management.schedulers.master import MasterScheduler
from tickit.core.state_interfaces.state_interface import get_interface
from tickit.core.typedefs import ComponentID
from tickit.utils.configuration.loading import read_configs

LOGGER = logging.getLogger(__name__)


class TickitSimulation:
    """A Tickit Simulation runner.

    Takes a master scheduler and componenents. When the run method is called
    scheduler and/or component tasks are created and awaited on.
    """

    _backend: str
    _scheduler: Optional[MasterScheduler]
    _components: Optional[Dict[ComponentID, Component]]

    def __init__(
        self,
        backend,
        scheduler,
        components,
    ) -> None:
        self._backend = backend
        self._scheduler = scheduler
        self._components = components

    async def run(self) -> None:
        """Awaits the scheduler and/or component tasks indefinitely."""
        tasks = list(self._start_tasks())
        if tasks:
            await asyncio.wait(tasks)

    def _start_tasks(self) -> Iterable[asyncio.Task]:
        yield from self._start_scheduler_tasks()
        yield from self._start_component_tasks()

    def _start_scheduler_tasks(self) -> Iterable[asyncio.Task]:
        if self._scheduler is not None:
            yield asyncio.create_task(self._scheduler.run_forever())

    def _start_component_tasks(self) -> Iterable[asyncio.Task]:
        if self._components is not None:
            for component in self._components.values():
                yield (
                    asyncio.create_task(
                        component.run_forever(*get_interface(self._backend))
                    )
                )


def build_simulation(
    config_path: str,
    backend: str = "internal",
    include_schedulers: bool = True,
    include_components: bool = True,
    components_to_run: Optional[Set[ComponentID]] = None,
) -> TickitSimulation:
    """Builds the master scheduler and components for a simulation.

        A config file is read, retrieving the relevant components. The wiring of
        these components is generated and used by to constuct the master scheduler.

    Args:
            config_path (str): The path to the configuration file.
            backend (str): The message broker to be used.
            include_schedulers (bool): A flag to determine if the master scheduler is
                included in the simulation. Defaults to True.
            include_components (bool): A flag to determine if components are included
                in the simulation. Defaults to True.
            components_to_run (Optional[Set[ComponentID]): A subset of components in
                the system to be run. Defaults to None, in which case all components
                will be run.

    Returns:
            TickitSimulation: A simulation object containing a given set of a scheduler
                and components which can be run.

    """
    components_to_run = components_to_run or set()

    configs = read_configs(config_path)
    inverse_wiring = InverseWiring.from_component_configs(configs)

    if include_schedulers:
        scheduler = MasterScheduler(inverse_wiring, *get_interface(backend))
    if include_components:
        components = {config.name: config() for config in configs}
        run_all = not components_to_run
        components = {
            config.name: config()
            for config in configs
            if run_all or config.name in components_to_run
        }

    return TickitSimulation(
        backend,
        scheduler if include_schedulers else None,
        components if include_components else None,
    )
