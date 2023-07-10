import asyncio
import logging
from typing import Set

import click
from click.core import Context

from tickit.core.simulation import TickitSimulationBuilder
from tickit.core.state_interfaces.state_interface import interfaces
from tickit.core.typedefs import ComponentID


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


@main.command(help="run one or more components without a scheduler")
@click.argument("components", nargs=-1)
@click.argument("config_path")
@click.option("--backend", default="kafka", type=click.Choice(list(interfaces(True))))
def components(config_path: str, components: Set[ComponentID], backend: str) -> None:
    """Runs one or more simulated components from a configuration file.

    If you pass it no componentID arguments it will run all of the components in the
    configuration file.

    Args:
        config_path (str): The path to the configuration file.
        components Set[ComponentID]: The name of the components to be run, seperated by
            whitespace.
        backend (str): The message broker to be used.
    """
    asyncio.run(
        TickitSimulationBuilder(
            config_path, backend, include_schedulers=False, components_to_run=components
        )
        .build()
        .run()
    )


@main.command(help="run the simulation scheduler")
@click.argument("config_path")
@click.option("--backend", default="kafka", type=click.Choice(list(interfaces(True))))
def scheduler(config_path: str, backend: str) -> None:
    """Runs the simulation master scheduler from a configuration file.

    Args:
        config_path (str): The path to the configuration file.
        backend (str): The message broker to be used.
    """
    asyncio.run(
        TickitSimulationBuilder(config_path, backend, include_components=False)
        .build()
        .run()
    )


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
    asyncio.run(TickitSimulationBuilder(config_path, backend).build().run())
