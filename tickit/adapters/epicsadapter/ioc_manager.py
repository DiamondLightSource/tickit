import asyncio
import itertools
import logging
from typing import List

from softioc import asyncio_dispatcher, builder, softioc

LOGGER = logging.getLogger(__name__)


_TICKIT_IOC_NAME: str = "TICKIT_IOC"
_REGISTERED_ADAPTER_IDS: List[int] = []
_ID_COUNTER: itertools.count = itertools.count()


def register_adapter() -> int:
    adapter_id = next(_ID_COUNTER)
    LOGGER.info(f"New IOC adapter registering with ID: {adapter_id}")
    _REGISTERED_ADAPTER_IDS.append(adapter_id)
    return adapter_id


def notify_adapter_ready(adapter_id: int) -> None:
    _REGISTERED_ADAPTER_IDS.remove(adapter_id)
    LOGGER.info(f"IOC adapter #{adapter_id} reports ready")
    if not _REGISTERED_ADAPTER_IDS:
        LOGGER.info("All registered adapters are ready, starting IOC")
        _build_and_run_ioc()


def _build_and_run_ioc() -> None:
    """Builds an EPICS python soft IOC for the adapter."""
    LOGGER.info("Initializing database")
    builder.SetDeviceName(_TICKIT_IOC_NAME)
    softioc.devIocStats(_TICKIT_IOC_NAME)
    builder.LoadDatabase()

    LOGGER.info("Starting IOC")
    event_loop = asyncio.get_event_loop()
    dispatcher = asyncio_dispatcher.AsyncioDispatcher(event_loop)
    softioc.iocInit(dispatcher)
    softioc.dbl()
    LOGGER.info("IOC started")
