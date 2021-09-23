import asyncio
import logging
from typing import cast

import click
from click.core import Context

from tickit.core.components.component import create_components
from tickit.core.lifetime_runnable import LifetimeRunnable, run_all_forever
from tickit.core.management.event_router import InverseWiring
from tickit.core.management.schedulers.master import MasterScheduler
from tickit.core.state_interfaces.state_interface import get_interface, interfaces
from tickit.utils.configuration.loading import read_configs


@click.group(invoke_without_command=True)
@click.version_option()
@click.option(
    "--log-level",
    default="DEBUG",
    type=click.Choice(["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]),
    help="The minimum level of severity for a log message to be printed to the console",
)
@click.pass_context
def main(ctx: Context, log_level: str):
    """The command line argument root, allowing for mode and log level configuration.

    Args:
        ctx (Context): The click context.
        log_level (str): The minimum logging level to be displayed.
    """
    logging.basicConfig(level=log_level)

    if ctx.invoked_subcommand is None:
        click.echo(main.get_help(ctx))


@main.command(help="run a single simulated component")
@click.argument("component")
@click.argument("config_path")
@click.option("--backend", default="kafka", type=click.Choice(list(interfaces(True))))
def component(config_path: str, component: str, backend: str) -> None:
    """Runs a single simulated component from a configuration file.

    Args:
        config_path (str): The path to the configuration file.
        component (str): The name of the component to be run.
        backend (str): The message broker to be used.
    """
    configs = read_configs(config_path)
    config = next(config for config in configs if config.name == component)
    components = create_components([config], *get_interface(backend))
    asyncio.run(run_all_forever(components))


@main.command(help="run the simulation scheduler")
@click.argument("config_path")
@click.option("--backend", default="kafka", type=click.Choice(list(interfaces(True))))
def scheduler(config_path: str, backend: str) -> None:
    """Runs the simulation master scheduler from a configuration file.

    Args:
        config_path (str): The path to the configuration file.
        backend (str): The message broker to be used.
    """
    configs = read_configs(config_path)
    inverse_wiring = InverseWiring.from_component_configs(configs)
    scheduler = MasterScheduler(inverse_wiring, *get_interface(backend))
    asyncio.run(run_all_forever([cast(LifetimeRunnable, scheduler)]))


@main.command(help="run a collection of devices with a scheduler")
@click.argument("config_path")
@click.option(
    "--backend", default="internal", type=click.Choice(list(interfaces(False)))
)
def all(config_path: str, backend: str) -> None:
    """Runs all components and the master scheduler from a configuration file.

    Args:
        config_path (str): The path to the configuration file.
        backend (str): The message broker to be used.
    """
    configs = read_configs(config_path)
    inverse_wiring = InverseWiring.from_component_configs(configs)
    scheduler = MasterScheduler(inverse_wiring, *get_interface(backend))
    components = create_components(configs, *get_interface(backend))
    asyncio.run(run_all_forever([cast(LifetimeRunnable, scheduler), *components]))
