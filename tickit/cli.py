import asyncio
import json
import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from typing import List, Tuple

from tickit import __version__
from tickit.core import DeviceSimulation
from tickit.core.event_router import Wiring
from tickit.core.lifetime_runnable import run_all_forever
from tickit.core.manager import Manager
from tickit.core.state_interfaces.internal import (
    InternalStateConsumer,
    InternalStateProducer,
    InternalStateTopicManager,
)
from tickit.core.state_interfaces.kafka import (
    KafkaStateConsumer,
    KafkaStateProducer,
    KafkaStateTopicManager,
)
from tickit.core.typedefs import DeviceConfig, DeviceID
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
parser_device.add_argument("-b", "--backend", default="kafka", choices=["kafka"])

parser_manager = subparsers.add_parser("manager")
parser_manager.add_argument("-b", "--backend", default="kafka", choices=["kafka"])

parser_all = subparsers.add_parser("all")
parser_all.add_argument("config_path", help="name given to device in simulation")
parser_all.add_argument(
    "-b", "--backend", default="internal", choices=["internal", "kafka"]
)

parser.add_argument("--version", action="version", version=__version__)


def main():
    args = parser.parse_args(sys.argv[1:])

    if args.backend == "internal":
        state_consumer = InternalStateConsumer
        state_producer = InternalStateProducer
        state_topic_manager = InternalStateTopicManager
    elif args.backend == "kafka":
        state_consumer = KafkaStateConsumer
        state_producer = KafkaStateProducer
        state_topic_manager = KafkaStateTopicManager

    if args.mode == "device":
        simulation = DeviceSimulation(
            args.device_name,
            import_class(args.device_class)(),
            state_consumer,
            state_producer,
        )
        asyncio.run(run_all_forever([simulation]))
    if args.mode == "manager":
        _, _, wiring = read_config(args.config_path)
        manager = Manager(wiring, state_consumer, state_producer, state_topic_manager,)
        asyncio.run(run_all_forever([manager]))
    if args.mode == "all":
        names, devices, wiring = read_config(args.config_path)
        device_simulations = [
            DeviceSimulation(name, device, state_consumer, state_producer)
            for name, device in zip(names, devices)
        ]
        manager = Manager(wiring, state_consumer, state_producer, state_topic_manager,)
        asyncio.run(run_all_forever([manager, *device_simulations]))


def read_config(config_path) -> Tuple[List[DeviceID], List[DeviceSimulation], Wiring]:
    configs = [DeviceConfig(**config) for config in json.load(open(config_path, "r"))]
    names = [config.name for config in configs]
    devices = [import_class(config.device_class)() for config in configs]
    wiring: Wiring = dict()
    for name, device in zip(names, devices):
        wiring[name] = {out_id: list() for out_id in device.initial_state[0].keys()}
    for config in configs:
        for in_id, (out_device, out_id) in config.inputs.items():
            wiring[out_device][out_id].append((config.name, in_id))

    return names, devices, wiring
