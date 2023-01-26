import asyncio
import itertools
import logging
from typing import Set

from softioc import asyncio_dispatcher, builder, softioc

LOGGER = logging.getLogger(__name__)

#: Name for the global Tickit IOC, will prefix some meta PVs.
_TICKIT_IOC_NAME: str = "TICKIT_IOC"

#: Ids of all adapters currently registered but not ready.
_REGISTERED_ADAPTER_IDS: Set[int] = set()

#: Iterator of unique IDs for new adapters
_ID_COUNTER: itertools.count = itertools.count()


def register_adapter() -> int:
    """Register a new adapter that may be creating records for the process-wide IOC.

    The IOC will not be initialized until all registered adapters have notified that
    they are ready.

    Returns:
        int: A unique ID for this adapter to use when notifiying that it is ready.
    """
    adapter_id = next(_ID_COUNTER)
    LOGGER.debug(f"New IOC adapter registering with ID: {adapter_id}")
    _REGISTERED_ADAPTER_IDS.add(adapter_id)
    return adapter_id


def notify_adapter_ready(adapter_id: int) -> None:
    """Notify the builder that a particular adpater has made all the records it needs.

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
    # dbl directly prints out all record names, so we have to check
    # the log level in order to only do it in DEBUG.
    if LOGGER.level <= logging.DEBUG:
        softioc.dbl()
    LOGGER.debug("IOC started")
