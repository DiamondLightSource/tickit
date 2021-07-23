from typing import AsyncIterator, Iterable, List, Optional, TypeVar

from tickit.utils.compat.typing_compat import Protocol, runtime_checkable

T = TypeVar("T")


@runtime_checkable
class StateConsumer(Protocol[T]):
    def __init__(self, consume_topics: Iterable[str]) -> None:
        ...

    async def consume(self,) -> AsyncIterator[Optional[T]]:
        if False:
            yield


@runtime_checkable
class StateProducer(Protocol[T]):
    def __init__(self) -> None:
        ...

    async def produce(self, topic: str, value: T) -> None:
        ...


@runtime_checkable
class StateTopicManager(Protocol):
    def __init__(self) -> None:
        ...

    async def get_topics(self) -> List[str]:
        ...

    async def create_topic(self, topic: str) -> None:
        ...

    async def remove_topic(self, topic: str) -> None:
        ...
