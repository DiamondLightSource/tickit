import json
from typing import Any, Dict, Iterable, List, NewType, Optional

Message = NewType("Message", bytes)
Messages = NewType("Messages", List[Message])


class Singleton(type):
    _instances = {}

    def __call__(self, *args: Any, **kwargs: Any) -> None:
        if self not in self._instances:
            self._instances[self] = super(Singleton, self).__call__(*args, **kwargs)
        return self._instances[self]


class InternalStateServer(metaclass=Singleton):
    _topics: Dict[str, Messages] = dict()

    def push(self, topic: str, message: Message) -> None:
        self._topics[topic].append(message)

    def poll(self, topic: str, offset: int) -> Messages:
        return self._topics[topic][offset:]

    def create_topic(self, topic: str) -> None:
        assert topic not in self._topics.keys()
        self._topics[topic] = list()

    def remove_topic(self, topic: str) -> None:
        assert topic in self._topics.keys()
        del self._topics[topic]

    @property
    def topics(self) -> List[str]:
        return list(self._topics.keys())


class InternalStateConsumer:
    def __init__(self, consume_topics: Iterable[str]) -> None:
        self.server = InternalStateServer()
        self.topics: Dict[str, int] = {topic: 0 for topic in consume_topics}
        self.messages: Messages = list()

    async def consume(self) -> Optional[object]:
        for topic, offset in self.topics.items():
            response = self.server.poll(topic, offset)
            self.topics[topic] += len(response)
            self.messages.extend(response)
        if self.messages:
            message = json.loads(self.messages.pop(0).decode("ascii"))
            print("Consumed {}".format(message))
            yield message
        else:
            yield None


class InternalStateProducer:
    def __init__(self) -> None:
        self.server = InternalStateServer()

    async def produce(self, topic: str, value: object) -> None:
        print("Producing {} to {}".format(value, topic))
        self.server.push(topic, json.dumps(value.__dict__).encode("ascii"))


class InternalStateTopicManager:
    def __init__(self) -> None:
        self.server = InternalStateServer()

    def get_topics(self) -> List[str]:
        return self.server.topics

    def create_topic(self, topic: str) -> None:
        self.server.create_topic(topic)

    def remove_topic(self, topic: str) -> None:
        self.server.remove_topic(topic)
