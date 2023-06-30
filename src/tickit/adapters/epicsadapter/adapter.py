import os
import re
from abc import abstractmethod
from dataclasses import dataclass
from tempfile import NamedTemporaryFile
from typing import Any, Callable, Dict, Optional, TypeVar

from softioc import builder, softioc

from tickit.core.adapter import Adapter, RaiseInterrupt

from .ioc_manager import notify_adapter_ready, register_adapter

#: Device type
D = TypeVar("D")


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


class EpicsAdapter(Adapter[D]):
    """An adapter implementation which acts as an EPICS IOC.

    This is optionally initialised from an EPICS database (db) file
    but can be customised in code by implementing on_db_load.
    """

    def __init__(self, ioc_name: str, db_file: Optional[str] = None) -> None:
        """An EpicsAdapter constructor which stores the db_file path and the IOC name.

        Args:
            ioc_name (str): The name of the EPICS IOC.
            db_file (str, optional): The path to the db_file.
        """
        self.db_file = db_file
        self.ioc_name = ioc_name
        self.interrupt_records: Dict[InputRecord, Callable[[], Any]] = {}
        self.ioc_num = register_adapter()

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
            print(f"Record {record.name} updated to : {current_value}")

    @abstractmethod
    def on_db_load(self) -> None:
        """Customises records that have been loaded in to suit the simulation."""
        raise NotImplementedError

    def load_records_without_DTYP_fields(self):
        """Load records from database file without DTYP fields."""
        with open(self.db_file, "rb") as inp:
            with NamedTemporaryFile(suffix=".db", delete=False) as out:
                for line in inp.readlines():
                    if not re.match(rb"\s*field\s*\(\s*DTYP", line):
                        out.write(line)

        softioc.dbLoadDatabase(out.name, substitutions=f"device={self.ioc_name}")
        os.unlink(out.name)

    async def run_forever(self, device: D, raise_interrupt: RaiseInterrupt) -> None:
        """Runs the server continuously."""
        await super().run_forever(device, raise_interrupt)
        builder.SetDeviceName(self.ioc_name)
        if self.db_file:
            self.load_records_without_DTYP_fields()
        self.on_db_load()
        builder.UnsetDevice()
        notify_adapter_ready(self.ioc_num)
