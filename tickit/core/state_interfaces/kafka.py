import json
from typing import AsyncIterator, Generic, Iterable, List, Optional

from kafka import KafkaConsumer
from kafka.admin import KafkaAdminClient
from kafka.admin.new_topic import NewTopic
from kafka.producer.kafka import KafkaProducer

from tickit.core.state_interfaces.state_interface import T


class KafkaStateConsumer(Generic[T]):
    def __init__(self, consume_topics: Iterable[str]) -> None:
        self.consumer = KafkaConsumer(
            *consume_topics,
            auto_offset_reset="earliest",
            value_deserializer=lambda m: json.loads(m.decode("ascii"))
        )

    async def consume(self) -> AsyncIterator[Optional[T]]:
        while True:
            partitions = self.consumer.poll(max_records=1)
            for records in partitions.values():
                for record in records:
                    print("Consumed {}".format(record.value))
                    yield record.value
            yield None


class KafkaStateProducer(Generic[T]):
    def __init__(self) -> None:
        self.producer = KafkaProducer(
            value_serializer=lambda m: json.dumps(m).encode("ascii")
        )

    async def produce(self, topic: str, value: T) -> None:
        print("Producing {} to {}".format(value, topic))
        self.producer.send(topic, value.__dict__)


class KafkaStateTopicManager:
    def __init__(self, num_partitions=1, replication_factor=1) -> None:
        self.num_partitions = num_partitions
        self.replication_factor = replication_factor
        self.admin_client = KafkaAdminClient()

    def get_topics(self) -> List[str]:
        return self.admin_client.list_topics()

    def create_topic(self, topic: str) -> None:
        topic = NewTopic(topic, self.num_partitions, self.replication_factor)
        self.admin_client.create_topics([topic])

    def remove_topic(self, topic: str) -> None:
        self.admin_client.delete_topics([topic])
