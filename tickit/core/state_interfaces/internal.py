import json
from collections import defaultdict
from typing import (
    AsyncIterator,
    DefaultDict,
    Dict,
    Generic,
    Iterable,
    List,
    NewType,
    Optional,
    TypeVar,
)

from tickit.core.state_interfaces import state_interface
from tickit.utils.singleton import Singleton

C = TypeVar("C")
P = TypeVar("P")

Message = NewType("Message", bytes)
Messages = NewType("Messages", List[Message])


class InternalStateServer(metaclass=Singleton):
    _topics: DefaultDict[str, Messages] = defaultdict(lambda: Messages(list()))

    def push(self, topic: str, message: Message) -> None:
        self._topics[topic].append(message)

    def poll(self, topic: str, offset: int) -> Messages:
        return Messages(self._topics[topic][offset:])

    def create_topic(self, topic: str) -> None:
        assert topic not in self._topics.keys()
        self._topics[topic] = Messages(list())

    def remove_topic(self, topic: str) -> None:
        assert topic in self._topics.keys()
        del self._topics[topic]

    @property
    def topics(self) -> List[str]:
        return list(self._topics.keys())


@state_interface.add("internal", False)
class InternalStateConsumer(Generic[C]):
    def __init__(self, consume_topics: Iterable[str]) -> None:
        self.server = InternalStateServer()
        self.topics: Dict[str, int] = {topic: 0 for topic in consume_topics}
        self.messages: Messages = Messages(list())

    async def consume(self) -> AsyncIterator[Optional[C]]:
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


@state_interface.add("internal", False)
class InternalStateProducer(Generic[P]):
    def __init__(self) -> None:
        self.server = InternalStateServer()

    async def produce(self, topic: str, value: P) -> None:
        print("Producing {} to {}".format(value, topic))
        self.server.push(topic, Message(json.dumps(value.__dict__).encode("ascii")))
