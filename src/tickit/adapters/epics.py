import asyncio
import itertools
import logging
from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, Generic, Optional, Set, TypeVar

from softioc import asyncio_dispatcher, builder, softioc

from tickit.core.adapter import RaiseInterrupt

LOGGER = logging.getLogger(__name__)

#: Name for the global Tickit IOC, will prefix some meta PVs.
_TICKIT_IOC_NAME: str = "TICKIT_IOC"

#: Ids of all adapters currently registered but not ready.
_REGISTERED_ADAPTER_IDS: Set[int] = set()

_REGISTERED_IOC_BACKGROUND_TASKS: Set[Awaitable[None]] = set()

#: Iterator of unique IDs for new adapters
_ID_COUNTER: itertools.count = itertools.count()


def register_adapter() -> int:
    """Register a new adapter that may be creating records for the process-wide IOC.

    The IOC will not be initialized until all registered adapters have notified that
    they are ready.

    Returns:
        int: A unique ID for this adapter to use when notifying that it is ready.
    """
    adapter_id = next(_ID_COUNTER)
    LOGGER.debug(f"New IOC adapter registering with ID: {adapter_id}")
    _REGISTERED_ADAPTER_IDS.add(adapter_id)
    return adapter_id


def register_background_task(task: Awaitable[None]) -> None:
    _REGISTERED_IOC_BACKGROUND_TASKS.add(task)

def notify_adapter_ready(adapter_id: int) -> None:
    """Notify the builder that a particular adapter has made all the records it needs.

    Once all registered adapters have notified, the IOC will start.

    Args:
        adapter_id (int): Unique ID of the adapter
    """
    _REGISTERED_ADAPTER_IDS.remove(adapter_id)
    LOGGER.debug(f"IOC adapter #{adapter_id} reports ready")
    if not _REGISTERED_ADAPTER_IDS:
        LOGGER.debug("All registered adapters are ready, starting IOC")
        _build_and_run_ioc()


def _build_and_run_ioc() -> None:
    """Build an EPICS python soft IOC for the adapter."""
    LOGGER.debug("Initializing database")

    # Records become immutable after this point
    builder.SetDeviceName(_TICKIT_IOC_NAME)
    softioc.devIocStats(_TICKIT_IOC_NAME)
    builder.LoadDatabase()

    LOGGER.debug("Starting IOC")
    event_loop = asyncio.get_event_loop()
    dispatcher = asyncio_dispatcher.AsyncioDispatcher(event_loop)
    softioc.iocInit(dispatcher)

    async def run_background_tasks() -> None:
        if len(_REGISTERED_IOC_BACKGROUND_TASKS) > 0:
            await asyncio.wait(_REGISTERED_IOC_BACKGROUND_TASKS)

    dispatcher(run_background_tasks)

    # dbl directly prints out all record names, so we have to check
    # the log level in order to only do it in DEBUG.
    if LOGGER.level <= logging.DEBUG:
        softioc.dbl()  # type: ignore
    LOGGER.debug("IOC started")

@dataclass(frozen=True)
class InputRecord:
    """A data container representing an EPICS input record."""

    name: str
    set: Callable
    get: Callable


@dataclass
class OutputRecord:
    """A data container representing an EPICS output record."""

    name: str


class EpicsAdapter:
    """An adapter interface for the EpicsIo."""

    interrupt_records: Dict[InputRecord, Callable[[], Any]]
    interrupt: RaiseInterrupt

    def __init__(self) -> None:
        self.interrupt_records = {}

    def float_rbv(
        self,
        name: str,
        getter: Callable[[], float],
        setter: Callable[[float], None],
        rbv_name: Optional[str] = None,
        precision: int = 2,
    ):
        rbv_name = rbv_name or f"{name}_RBV"
        builder.aOut(
            name,
            initial_value=getter(),
            on_update=self.interrupting_callback(setter),
            PREC=precision,
        )
        rbv = builder.aIn(rbv_name, initial_value=getter(), PREC=precision,)
        self.link_input_on_interrupt(rbv, getter)

    def float_ro(self, name: str, getter: Callable[[], float], precision: int = 2,):
        self.link_input_on_interrupt(
            builder.aIn(name, PREC=precision),
            getter,
        )

    def int_rbv(
        self,
        name: str,
        getter: Callable[[], int],
        setter: Callable[[int], None],
        rbv_name: Optional[str] = None,
    ):
        rbv_name = rbv_name or f"{name}_RBV"
        builder.mbbOut(
            name,
            initial_value=getter(),
            on_update=self.interrupting_callback(setter),
        )
        rbv = builder.mbbIn(rbv_name, initial_value=getter())
        self.link_input_on_interrupt(rbv, getter)

    def bool_rbv(
        self,
        name: str,
        getter: Callable[[], bool],
        setter: Callable[[bool], None],
        rbv_name: Optional[str] = None,
    ):
        rbv_name = rbv_name or f"{name}_RBV"
        builder.boolOut(
            name,
            initial_value=getter(),
            on_update=self.interrupting_callback(setter),
        )
        rbv = builder.boolIn(rbv_name, initial_value=getter())
        self.link_input_on_interrupt(rbv, getter)

    def bool_ro(self, name: str, getter: Callable[[], float]):
        self.link_input_on_interrupt(
            builder.boolIn(name),
            getter,
        )

    def interrupting_callback(
        self, action: Callable[[Any], None]
    ) -> Callable[[Any], Awaitable[None]]:
        async def callback(value: Any) -> None:
            action(value)
            await self.interrupt()

        return callback

    def link_input_on_interrupt(
        self, record: InputRecord, getter: Callable[[], Any]
    ) -> None:
        """Adds a record and a getter to the mapping of interrupting records.

        Args:
            record (InputRecord): The record to be added.
            getter (Callable[[], Any]): The getter handle.
        """
        self.interrupt_records[record] = getter

    @abstractmethod
    def on_db_load(self) -> None:
        """Customises records that have been loaded in to suit the simulation."""
        raise NotImplementedError

    def after_update(self) -> None:
        """Updates IOC records immediately following a device update."""
        for record, getter in self.interrupt_records.items():
            current_value = getter()
            record.set(current_value)
            print(f"Record {record.name} updated to : {current_value}")

    def polling_interrupt(self, interval: float) -> None:
        async def polling_task() -> None:
            while True:
                await asyncio.sleep(interval)
                await self.interrupt()
        
        register_background_task(polling_task())
