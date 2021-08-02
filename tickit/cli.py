import asyncio
from typing import Iterable, List, Tuple

import click
import yaml
from click.core import Context

from tickit.core.device import DeviceConfig
from tickit.core.device_simulation import DeviceSimulation
from tickit.core.event_router import InverseWiring
from tickit.core.lifetime_runnable import run_all_forever
from tickit.core.manager import Manager
from tickit.core.state_interfaces.state_interface import get_interface, interfaces


@click.group(invoke_without_command=True)
@click.version_option()
@click.pass_context
def main(ctx: Context):

    if ctx.invoked_subcommand is None:
        click.echo(main.get_help(ctx))


@main.command(help="run a single simulated device")
@click.argument("device")
@click.argument("config_path")
@click.option("--backend", default="kafka", type=click.Choice(interfaces(True)))
def device(config_path, device, backend):
    configs = read_configs(config_path)
    config = next(config for config in configs if config.name == device)
    device_simulations = create_device_simulations([config], backend)
    asyncio.run(run_all_forever(device_simulations))


@main.command(help="run the simulation manager")
@click.argument("config_path")
@click.option("--backend", default="kafka", type=click.Choice(interfaces(True)))
def manager(config_path, backend):
    configs = read_configs(config_path)
    inverse_wiring = build_inverse_wiring(configs)
    manager = Manager(inverse_wiring, *get_interface(backend))
    asyncio.run(run_all_forever([manager]))


@main.command(help="run a collection of devices with a manager")
@click.argument("config_path")
@click.option("--backend", default="internal", type=click.Choice(interfaces(False)))
def all(config_path, backend):
    configs = read_configs(config_path)
    inverse_wiring = build_inverse_wiring(configs)
    manager = Manager(inverse_wiring, *get_interface(backend))
    device_simulations = create_device_simulations(configs, backend)
    asyncio.run(run_all_forever([manager, *device_simulations]))


def read_configs(config_path) -> Tuple[List[DeviceConfig], InverseWiring]:
    return yaml.load(open(config_path, "r"), Loader=yaml.Loader)


def build_inverse_wiring(configs: Iterable[DeviceConfig]) -> InverseWiring:
    return InverseWiring({config.name: config.inputs for config in configs})


def create_device_simulations(
    configs: Iterable[DeviceConfig], backend: str
) -> List[DeviceSimulation]:
    return [DeviceSimulation(config, *get_interface(backend)) for config in configs]
