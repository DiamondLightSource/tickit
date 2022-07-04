import asyncio
import itertools
import logging
import os
import re
import threading
from abc import abstractmethod
from dataclasses import dataclass
from tempfile import NamedTemporaryFile
from typing import Any, Callable, Dict, List

from softioc import asyncio_dispatcher, builder, softioc

from tickit.core.adapter import Adapter, RaiseInterrupt
from tickit.core.device import Device

LOGGER = logging.getLogger(__name__)


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


class IocSingleton:
    _ioc_name: str
    _reg: List[int]
    _id_counter: itertools.count

    def __init__(self, ioc_name: str) -> None:
        self._ioc_name = ioc_name
        self._reg = []
        self._id_counter = itertools.count()

    def register_adapter(self) -> int:
        adapter_id = next(self._id_counter)
        LOGGER.info(f"New IOC adapter registering with ID: {adapter_id}")
        self._reg.append(adapter_id)
        return adapter_id

    def notify_adapter_ready(self, adapter_id: int) -> None:
        self._reg.remove(adapter_id)
        LOGGER.info(f"IOC adapter #{adapter_id} reports ready")
        if not self._reg:
            LOGGER.info("All registered adapters are ready, starting IOC")
            self.build_ioc()

    def build_ioc(self) -> None:
        """Builds an EPICS python soft IOC for the adapter."""
        LOGGER.info("Initializing database")
        builder.SetDeviceName(self._ioc_name)
        softioc.devIocStats(self._ioc_name)
        builder.LoadDatabase()

        LOGGER.info("Starting IOC")
        event_loop = asyncio.get_event_loop()
        dispatcher = asyncio_dispatcher.AsyncioDispatcher(event_loop)
        softioc.iocInit(dispatcher)
        softioc.dbl()
        LOGGER.info("IOC started")


_IOC_SINGLETON = IocSingleton("TICKIT_IOC")


class EpicsAdapter(Adapter):
    """An adapter implementation which acts as an EPICS IOC."""

    def __init__(self, db_file: str, ioc_name: str) -> None:
        """An EpicsAdapter constructor which stores the db_file path and the IOC name.

        Args:
            db_file (str): The path to the db_file.
            ioc_name (str): The name of the EPICS IOC.
        """
        self.db_file = db_file
        self.ioc_name = ioc_name
        self.interrupt_records: Dict[InputRecord, Callable[[], Any]] = {}
        self.ioc_num = _IOC_SINGLETON.register_adapter()

    def link_input_on_interrupt(
        self, record: InputRecord, getter: Callable[[], Any]
    ) -> None:
        """Adds a record and a getter to the mapping of interrupting records.

        Args:
            record (InputRecord): The record to be added.
            getter (Callable[[], Any]): The getter handle.
        """
        self.interrupt_records[record] = getter

    def after_update(self) -> None:
        """Updates IOC records immediately following a device update."""
        for record, getter in self.interrupt_records.items():
            current_value = getter()
            record.set(current_value)
            print("Record {} updated to : {}".format(record.name, current_value))

    @abstractmethod
    def on_db_load(self) -> None:
        """Customises records that have been loaded in to suit the simulation."""
        raise NotImplementedError

    def load_records_without_DTYP_fields(self):
        """Loads the records without DTYP fields."""
        with open(self.db_file, "rb") as inp:
            with NamedTemporaryFile(suffix=".db", delete=False) as out:
                for line in inp.readlines():
                    if not re.match(rb"\s*field\s*\(\s*DTYP", line):
                        out.write(line)

        softioc.dbLoadDatabase(out.name, substitutions=f"device={self.ioc_name}")
        os.unlink(out.name)

    async def run_forever(
        self, device: Device, raise_interrupt: RaiseInterrupt
    ) -> None:
        """Runs the server continously."""
        await super().run_forever(device, raise_interrupt)
        self.load_records_without_DTYP_fields()
        self.on_db_load()
        _IOC_SINGLETON.notify_adapter_ready(self.ioc_num)
