import asyncio
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from tickit import __version__
from tickit.core import DeviceSimulation
from tickit.core.event_router import Wiring
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
parser_device.add_argument("-b", "--backend", default="kafka", choices=["kafka"])

parser_manager = subparsers.add_parser("manager")
parser_manager.add_argument("-b", "--backend", default="kafka", choices=["kafka"])

parser_all = subparsers.add_parser("all")
parser_all.add_argument(
    "-b", "--backend", default="internal", choices=["internal", "kafka"]
)

parser.add_argument("--version", action="version", version=__version__)


async def main(args):
    args = parser.parse_args(args)
    print(args)
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
        await asyncio.wait([asyncio.create_task(simulation.run_forever())])
    if args.mode == "manager":
        manager = Manager(
            Wiring({"random-trampoline": {"output": [("sink", "input")]}}),
            state_consumer,
            state_producer,
            state_topic_manager,
        )
        await asyncio.wait([asyncio.create_task(manager.run_forever())])
    if args.mode == "all":
        manager = Manager(
            Wiring({"random-trampoline": {"output": [("sink", "input")]}}),
            state_consumer,
            state_producer,
            state_topic_manager,
        )
        trampoline = DeviceSimulation(
            "random-trampoline", RandomTrampoline(), state_consumer, state_producer,
        )
        sink = DeviceSimulation("sink", Sink(), state_consumer, state_producer,)
        tasks = [
            asyncio.create_task(manager.run_forever()),
            asyncio.create_task(trampoline.run_forever()),
            asyncio.create_task(sink.run_forever()),
        ]
        await asyncio.wait(tasks)
