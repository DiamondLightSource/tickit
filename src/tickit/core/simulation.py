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
        componets,
    ) -> None:
        self._backend = backend
        self._scheduler = scheduler
        self._components = componets

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


class TickitSimulationBuilder:
    """A Ticket simulation builder.

    A utility class that uses a config file to create a scheduler and the components
    for a simulation.
    """

    _backend: str
    _config_path: str

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
        """Instantiate the builder class variables.

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

        """
        self._backend = backend
        self._config_path = config_path

        self._include_schedulers = include_schedulers
        self._include_components = include_components
        self._components_to_run = components_to_run or set()

    def build(self) -> TickitSimulation:
        """Builds the master scheduler and components for a simulation.

        A config file is read, retrieving the relevant components. The wiring of
        these components is generated and used by the master scheduler for event
        routing.

        Returns:
            TickitSimulation: A simulation object containing a given set of a scheduler
                and components which can be run.

        """
        configs = read_configs(self._config_path)
        inverse_wiring = InverseWiring.from_component_configs(configs)
        scheduler = MasterScheduler(inverse_wiring, *get_interface(self._backend))
        components = {config.name: config() for config in configs}

        components = {
            config.name: config()
            for config in configs
            if config.name
            in (
                self._components_to_run
                if self._components_to_run
                else (config.name for config in configs)
            )
        }

        return TickitSimulation(
            self._backend,
            scheduler if self._include_schedulers else None,
            components if self._include_components else None,
        )
