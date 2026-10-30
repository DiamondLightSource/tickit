"""Interface for ``python -m tickit``."""

import asyncio
import logging
from typing import Annotated, Literal

import typer
from typer import Context

from tickit import __version__
from tickit.core.simulation import build_simulation
from tickit.core.state_interfaces.state_interface import interfaces
from tickit.core.typedefs import ComponentID

app = typer.Typer(name="tickit")


def _backend_callback(value: str) -> str:
    """Validate backend choice at runtime."""
    valid = list(interfaces(True))
    if value not in valid:
        raise typer.BadParameter(
            f"Invalid backend '{value}'. Choose from: {', '.join(valid)}"
        )
    return value


def version_callback(value: bool):
    """Print version and exit."""
    if value:
        print(f"tickit, version: {__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    # Can't use `Context | None` — typer detects ctx via isinstance(annotation, type)
    # which fails on Union types; see
    # https://github.com/fastapi/typer/blob/master/typer/main.py#L1382
    ctx: Context = None,  # type: ignore[assignment]
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            callback=version_callback,
            is_eager=True,
            help="Show version of techui-builder and exit",
        ),
    ] = False,
    log_level: Annotated[
        Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"],
        typer.Option(
            "--log-level",
            help="Minimum logging level severity to display to console",
        ),
    ] = "DEBUG",
):
    """Configure mode and log level."""
    logging.basicConfig(level=log_level)

    if ctx is None or ctx.invoked_subcommand is None:
        typer.echo(app.rich_help_panel)


@app.command(help="run one or more components without a scheduler")
def components(
    config_path: Annotated[str, typer.Argument()],
    components: Annotated[list[str] | None, typer.Argument()] = None,
    backend: Annotated[
        str, typer.Option("--backend", callback=_backend_callback)
    ] = "kafka",
) -> None:
    """Run one or more simulated components from a configuration file.

    If you pass it no componentID arguments it will run all of the components in the
    configuration file.

    Args:
        config_path (str): The path to the configuration file.
        components (list[str]): The name of the components to be run,
        seperated by whitespace. If none are provided, all components will be run.
        backend (str): The message broker to be used.

    """
    components_to_run: set[ComponentID] | None
    if components is None:
        components = []
    if not components:
        components_to_run = None
    else:
        components_to_run = {ComponentID(c) for c in components}

    asyncio.run(
        build_simulation(
            config_path,
            backend,
            include_schedulers=False,
            components_to_run=components_to_run,
        ).run()
    )


@app.command(help="run the simulation scheduler")
def scheduler(
    config_path: Annotated[str, typer.Argument()],
    backend: Annotated[
        str, typer.Option("--backend", callback=_backend_callback)
    ] = "kafka",
) -> None:
    """Run the master scheduler from a configuration file.

    Args:
        config_path (str): The path to the configuration file.
        backend (str): The message broker to be used.

    """
    asyncio.run(build_simulation(config_path, backend, include_components=False).run())


@app.command(help="run a collection of devices with a scheduler")
def all(
    config_path: Annotated[str, typer.Argument()],
    backend: Annotated[
        str, typer.Option("--backend", callback=_backend_callback)
    ] = "kafka",
) -> None:
    """Run all components and the master scheduler from a configuration file.

    Args:
        config_path (str): The path to the configuration file.
        backend (str): The message broker to be used.

    """
    asyncio.run(build_simulation(config_path, backend).run())


if __name__ == "__main__":
    app()
