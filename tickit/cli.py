import asyncio
import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from typing import List, Tuple

import yaml

from tickit import __version__
from tickit.core import DeviceSimulation
from tickit.core.adapter import Adapter
from tickit.core.device import Device
from tickit.core.event_router import InverseWiring
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
from tickit.utils.dynamic_import import import_class

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
parser_manager.add_argument("config_path", help="path to simulation configuration json")
parser_manager.add_argument("-b", "--backend", default="kafka", choices=["kafka"])

parser_all = subparsers.add_parser("all")
parser_all.add_argument("config_path", help="path to simulation configuration json")
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
        _, _, _, wiring = read_config(args.config_path)
        manager = Manager(wiring, state_consumer, state_producer, state_topic_manager,)
        asyncio.run(run_all_forever([manager]))
    if args.mode == "all":
        names, devices, adapterss, wiring = read_config(args.config_path)
        device_simulations = [
            DeviceSimulation(name, device, adapters, state_consumer, state_producer)
            for name, device, adapters in zip(names, devices, adapterss)
        ]
        manager = Manager(wiring, state_consumer, state_producer, state_topic_manager,)
        asyncio.run(run_all_forever([manager, *device_simulations]))


def read_config(
    config_path,
) -> Tuple[List[DeviceID], List[Device], List[List[Adapter]], InverseWiring]:
    configs: List[DeviceConfig] = yaml.load(open(config_path, "r"), Loader=yaml.Loader)
    names = [config.name for config in configs]
    devices: List[Device] = [import_class(config.device_class) for config in configs]
    adapterss: List[List[Adapter]] = [
        [import_class(adapter.adapter_class) for adapter in config.adapters]
        for config in configs
    ]
    inverse_wiring = InverseWiring({config.name: config.inputs for config in configs})
    return names, devices, adapterss, inverse_wiring
