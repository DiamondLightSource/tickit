import asyncio
import json
from typing import AsyncIterator, Generic, Iterable, Optional, TypeVar

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from tickit.core.state_interfaces import state_interface

C = TypeVar("C")
P = TypeVar("P")


@state_interface.add("kafka", True)
class KafkaStateConsumer(Generic[C]):
    def __init__(self, consume_topics: Iterable[str]) -> None:
        self.consumer = AIOKafkaConsumer(
            *consume_topics,
            auto_offset_reset="earliest",
            value_deserializer=lambda m: json.loads(m.decode("ascii"))
        )
        asyncio.create_task(self.consumer.start())

    async def consume(self) -> AsyncIterator[Optional[C]]:
        async for message in self.consumer:
            print("Consumed {}".format(message))
            yield message
        yield None


@state_interface.add("kafka", True)
class KafkaStateProducer(Generic[P]):
    def __init__(self) -> None:
        self.producer = AIOKafkaProducer(
            value_serializer=lambda m: json.dumps(m).encode("ascii")
        )

    async def produce(self, topic: str, value: P) -> None:
        print("Producing {} to {}".format(value, topic))
        self.producer.send(topic, value.__dict__)
