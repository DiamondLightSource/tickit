import asyncio
from typing import AsyncIterator, Generic, Iterable, Optional, TypeVar

import yaml
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from yaml.loader import Loader

from tickit.core.state_interfaces import state_interface

C = TypeVar("C")
P = TypeVar("P")


@state_interface.add("kafka", True)
class KafkaStateConsumer(Generic[C]):
    def __init__(self, consume_topics: Iterable[str]) -> None:
        self.consumer = AIOKafkaConsumer(
            *consume_topics,
            auto_offset_reset="earliest",
            value_deserializer=lambda m: yaml.load(m.decode("utf-8"), Loader=Loader)
        )
        self._start = asyncio.create_task(self.consumer.start())

    async def consume(self) -> AsyncIterator[Optional[C]]:
        await self._start
        paritions = await self.consumer.getmany()
        for _, records in paritions.items():
            for record in records:
                print("Consumed {}".format(record.value))
                yield record.value
        yield None


@state_interface.add("kafka", True)
class KafkaStateProducer(Generic[P]):
    def __init__(self) -> None:
        self.producer = AIOKafkaProducer(
            value_serializer=lambda m: yaml.dump(m).encode("utf-8")
        )
        self._start = asyncio.create_task(self.producer.start())

    async def produce(self, topic: str, value: P) -> None:
        await self._start
        print("Producing {} to {}".format(value, topic))
        await self.producer.send(topic, value)
