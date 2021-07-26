import asyncio
import json
from typing import AsyncIterator, Generic, Iterable, List, Optional

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from tickit.core.state_interfaces.state_interface import T


class KafkaStateConsumer(Generic[T]):
    def __init__(self, consume_topics: Iterable[str]) -> None:
        self.consumer = AIOKafkaConsumer(
            *consume_topics,
            auto_offset_reset="earliest",
            value_deserializer=lambda m: json.loads(m.decode("ascii"))
        )
        asyncio.create_task(self.consumer.start())

    async def consume(self) -> AsyncIterator[Optional[T]]:
        async for message in self.consumer:
            print("Consumed {}".format(message))
            yield message
        yield None


class KafkaStateProducer(Generic[T]):
    def __init__(self) -> None:
        self.producer = AIOKafkaProducer(
            value_serializer=lambda m: json.dumps(m).encode("ascii")
        )

    async def produce(self, topic: str, value: T) -> None:
        print("Producing {} to {}".format(value, topic))
        self.producer.send(topic, value.__dict__)


class KafkaStateTopicManager:
    async def get_topics(self) -> List[str]:
        raise NotImplementedError

    async def create_topic(self, topic: str) -> None:
        pass

    async def remove_topic(self, topic: str) -> None:
        pass
