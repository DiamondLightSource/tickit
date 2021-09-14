from asyncio import PriorityQueue
from typing import Generic, Iterable, List, Tuple, TypeVar

#: Queue content type
T = TypeVar("T")


class ManyAsyncPriorityQueue(PriorityQueue, Generic[T]):
    """A asynchronous priority queue of for tuples of priority and any type"""

    async def get(self) -> Tuple[int, T]:
        """Wait until an item is avaiable, remove and return it from the queue

        Returns:
            Tuple[int, T]: A tuple of priority and the item removed from the queue
        """
        return await super().get()

    async def get_all_tie(self) -> Tuple[int, List[T]]:
        """Wait until an item is avaiable, remove and return all items of equal priority

        Returns:
            Tuple[int, List[T]]: A tuple of the priority and all items of that priority
        """
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
        """Wait until a free slot is available, put the item into the queue

        Args:
            item (Tuple[int, T]): A tuple of priority and the item to be added to the
                queue
        """
        return await super().put(item)

    async def put_many(self, items: Iterable[Tuple[int, T]]) -> None:
        """Wait until free slots are available, put items into the queue

        Args:
            items (Iterable[Tuple[int, T]]): An iterable of tuples of priority and
                items to be added to the queue
        """
        for item in items:
            await self.put(item)

    async def all_lt(self, priority: int) -> List[T]:
        """Remove and return all items of priority less than or equal to the speicified value

        Args:
            priority (int): The maximum priority of items which should be returned

        Returns:
            List[T]:
                A list of items with priority less than or equal to the specified value
        """
        values: List[T] = list()
        while not self.empty():
            next: Tuple[int, List[T]] = await self.get_all_tie()
            if not next[0] <= priority:
                self.put_many((next[0], value) for value in next[1])
            values.extend(next[1])
        return values
