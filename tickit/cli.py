import asyncio
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from tickit import __version__
from tickit.core import DeviceSimulation
from tickit.core.event_router import Wiring
from tickit.core.manager import Manager
from tickit.devices.toy import RandomTrampoline, Sink
from tickit.utils import import_class

parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter)

subparsers = parser.add_subparsers(
    title="mode",
    dest="mode",
    description="device: run a single simulated device.\n"
    + "manager: run the simulation manager\n"
    + "all: run a collection of devices with a manager",
)

parser_device = subparsers.add_parser("device")
parser_device.add_argument("device_name", help="name given to device in simulation")
parser_device.add_argument(
    "device_class", help="dotted path of device e.g: tickit.devices.eiger.Eiger"
)

parser_manager = subparsers.add_parser("manager")

parser_all = subparsers.add_parser("all")
# parser_all.add_argument("config_path", help="path to config file")

parser.add_argument("--version", action="version", version=__version__)


async def main(args):
    args = parser.parse_args(args)
    print(args)
    if args.mode == "device":
        simulation = DeviceSimulation(
            args.device_name, import_class(args.device_class)()
        )
        await asyncio.wait([asyncio.create_task(simulation.run_forever())])
    if args.mode == "manager":
        manager = Manager(
            Wiring({"random-trampoline": {"output": [("sink", "input")]}})
        )
        await asyncio.wait([asyncio.create_task(manager.run_forever())])
    if args.mode == "all":
        manager = Manager(
            Wiring({"random-trampoline": {"output": [("sink", "input")]}})
        )
        trampoline = DeviceSimulation("random-trampoline", RandomTrampoline())
        sink = DeviceSimulation("sink", Sink())
        tasks = [
            asyncio.create_task(manager.run_forever()),
            asyncio.create_task(trampoline.run_forever()),
            asyncio.create_task(sink.run_forever()),
        ]
        await asyncio.wait(tasks)
