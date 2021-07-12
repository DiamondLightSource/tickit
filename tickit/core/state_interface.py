from typing import Iterable, List, Optional, Protocol, runtime_checkable


@runtime_checkable
class StateConsumer(Protocol):
    def __init__(self, consume_topics: Iterable[str]) -> None:
        ...

    async def consume(self) -> Optional[object]:
        ...


@runtime_checkable
class StateProducer(Protocol):
    def __init__(self) -> None:
        ...

    async def produce(self, topic: str, value: object) -> None:
        ...


@runtime_checkable
class StateTopicManager(Protocol):
    def __init__(self) -> None:
        ...

    def get_topics(self) -> List[str]:
        ...

    def create_topic(self, topic: str) -> None:
        ...

    def remove_topic(self, topic: str) -> None:
        ...
