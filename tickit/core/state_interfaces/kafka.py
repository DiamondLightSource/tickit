import asyncio
from typing import Awaitable, Callable, Generic, Iterable, TypeVar

import yaml
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from yaml.loader import Loader

from tickit.core.state_interfaces import state_interface

C = TypeVar("C")
P = TypeVar("P")


@state_interface.add("kafka", True)
class KafkaStateConsumer(Generic[C]):
    def __init__(self, callback: Callable[[C], Awaitable[None]]) -> None:
        self.consumer = AIOKafkaConsumer(
            None,
            auto_offset_reset="earliest",
            value_deserializer=lambda m: yaml.load(m.decode("utf-8"), Loader=Loader),
        )
        self.callback = callback
        asyncio.create_task(self.run_forever())

    async def subscribe(self, topics: Iterable[str]):
        self.consumer.subscribe(topics)

    async def run_forever(self) -> None:
        await self.consumer.start()
        while True:
            async for message in self.consumer:
                await self.callback(message.value)


@state_interface.add("kafka", True)
class KafkaStateProducer(Generic[P]):
    def __init__(self) -> None:
        self.producer = AIOKafkaProducer(
            value_serializer=lambda m: yaml.dump(m).encode("utf-8")
        )
        self._start = asyncio.create_task(self.producer.start())

    async def produce(self, topic: str, value: P) -> None:
        await self._start
        await self.producer.send(topic, value)
