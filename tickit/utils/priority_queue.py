from asyncio import PriorityQueue
from typing import Generic, Iterable, List, Tuple, TypeVar

T = TypeVar("T")


class ManyAsyncPriorityQueue(PriorityQueue, Generic[T]):
    async def get(self) -> Tuple[int, T]:
        return await super().get()

    async def get_all_tie(self) -> Tuple[int, List[T]]:
        priority, value = await self.get()
        values: List[T] = [value]
        while not self.empty():
            next_priority, next_value = self.get_nowait()
            if next_priority != priority:
                await self.put((next_priority, next_value))
                break
            values.append(next_value)

        return priority, values

    async def put(self, item: Tuple[int, T]) -> None:
        return await super().put(item)

    async def put_many(self, items: Iterable[Tuple[int, T]]) -> None:
        for item in items:
            await self.put(item)

    async def all_lt(self, priority: int) -> List[T]:
        values: List[T] = list()
        while not self.empty():
            next: Tuple[int, List[T]] = await self.get_all_tie()
            if not next[0] <= priority:
                self.put_many((next[0], value) for value in next[1])
            values.extend(next[1])
        return values
