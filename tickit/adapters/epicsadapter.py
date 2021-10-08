import asyncio
import os
import re
from abc import abstractmethod
from dataclasses import dataclass
from tempfile import NamedTemporaryFile
from typing import Any, Callable, Dict

from softioc import asyncio_dispatcher, builder, softioc

from tickit.core.adapter import Adapter, RaiseInterrupt
from tickit.core.device import Device


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

    def build_ioc(self) -> None:
        """Builds an EPICS python soft IOC for the adapter."""
        builder.SetDeviceName(self.ioc_name)

        self.load_records_without_DTYP_fields()
        self.on_db_load()

        softioc.devIocStats(self.ioc_name)

        builder.LoadDatabase()
        event_loop = asyncio.get_event_loop()
        dispatcher = asyncio_dispatcher.AsyncioDispatcher(event_loop)
        softioc.iocInit(dispatcher)

    async def run_forever(
        self, device: Device, raise_interrupt: RaiseInterrupt
    ) -> None:
        """Runs the server continously."""
        await super().run_forever(device, raise_interrupt)
        self.build_ioc()
