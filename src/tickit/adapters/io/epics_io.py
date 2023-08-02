import os
import re
from tempfile import NamedTemporaryFile
from typing import Any, Callable, Dict, Optional

from softioc import builder, softioc

from tickit.adapters.epics import (
    EpicsAdapter,
    InputRecord,
    notify_adapter_ready,
    register_adapter,
)
from tickit.core.adapter import AdapterIo, RaiseInterrupt


class EpicsIo(AdapterIo[EpicsAdapter]):
    """An AdapterIo implementation which acts as an EPICS IOC.

    This is optionally initialised from an EPICS database (db) file
    but can be customised in code by implementing on_db_load in EpicsAdapter.
    """

    interrupt_records: Dict[InputRecord, Callable[[], Any]] = {}

    def __init__(self, ioc_name: str, db_file: Optional[str] = None) -> None:
        """An EpicsAdapter constructor which stores the db_file path and the IOC name.

        Args:
            ioc_name (str): The name of the EPICS IOC.
            db_file (str, optional): The path to the db_file.
        """
        self.db_file = db_file
        self.ioc_name = ioc_name
        self.ioc_num = register_adapter()

    async def setup(
        self, adapter: EpicsAdapter, raise_interrupt: RaiseInterrupt
    ) -> None:
        self.interrupt_records = adapter.interrupt_records
        adapter.interrupt = raise_interrupt

        builder.SetDeviceName(self.ioc_name)
        if self.db_file:
            self.load_records_without_DTYP_fields()
        adapter.on_db_load()
        builder.UnsetDevice()
        notify_adapter_ready(self.ioc_num)

    def load_records_without_DTYP_fields(self):
        """Load records from database file without DTYP fields."""
        if self.db_file:
            with open(self.db_file, "rb") as inp:
                with NamedTemporaryFile(suffix=".db", delete=False) as out:
                    for line in inp.readlines():
                        if not re.match(rb"\s*field\s*\(\s*DTYP", line):
                            out.write(line)

            softioc.dbLoadDatabase(out.name, substitutions=f"device={self.ioc_name}")
            os.unlink(out.name)
