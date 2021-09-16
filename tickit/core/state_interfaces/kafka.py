import asyncio
from typing import Awaitable, Callable, Generic, Iterable, TypeVar

import yaml
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from yaml.loader import Loader

from tickit.core.state_interfaces import state_interface

#: A consumable value
C = TypeVar("C")
#: A producable value
P = TypeVar("P")


@state_interface.add("kafka", True)
class KafkaStateConsumer(Generic[C]):
    """A kafka implementation of the StateConsumer protocol.

    A kafka implementation of the StateConsumer protocol, this consumer can subscribe
    to kafka topics, upon recieving a message the consumer passes the value to the
    callback function passed during initialization, if a topic is subscribed to which
    does not yet exist it is created.
    """

    def __init__(self, callback: Callable[[C], Awaitable[None]]) -> None:
        """Creates an AIOKafka Consumer and begins consuming subscribed topics.

        Args:
            callback (Callable[[C], Awaitable[None]]): An asynchronous handler function
                for consumed values.
        """

        async def run_forever() -> None:
            await self.consumer.start()
            while True:
                async for message in self.consumer:
                    await self.callback(message.value)

        self.consumer = AIOKafkaConsumer(
            None,
            auto_offset_reset="earliest",
            value_deserializer=lambda m: yaml.load(m.decode("utf-8"), Loader=Loader),
        )
        self.callback = callback
        asyncio.create_task(run_forever())

    async def subscribe(self, topics: Iterable[str]):
        """Subscribes the consumer to the given topics, new messages are passed to the callback.

        Args:
            topics (Iterable[str]): An iterable of topics to subscribe to.
        """
        self.consumer.subscribe(topics)


@state_interface.add("kafka", True)
class KafkaStateProducer(Generic[P]):
    """A kafka implementation of the StateProducer protocol.

    A kafka implementation of the StateProducer protocol, this producer can produce a
    value to a kafka topic, if the topic does not yet exist it is created.
    """

    def __init__(self) -> None:
        """Creates and starts and AIOKafka Producer."""
        self.producer = AIOKafkaProducer(
            value_serializer=lambda m: yaml.dump(m).encode("utf-8")
        )
        self._start = asyncio.create_task(self.producer.start())

    async def produce(self, topic: str, value: P) -> None:
        """Produces a value to the provided topic.

        Args:
            topic (str): The topic to which the value should be sent.
            value (P): The value to send to the provided topic.
        """
        await self._start
        await self.producer.send(topic, value)
