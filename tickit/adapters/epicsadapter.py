import asyncio
import os
import re
from dataclasses import dataclass
from tempfile import NamedTemporaryFile
from typing import Any, Callable, Dict

from softioc import asyncio_dispatcher, builder, softioc

from tickit.core.adapter import ConfigurableAdapter


@dataclass
class InputRecord:
    name: str
    set: Callable
    get: Callable


@dataclass
class OutputRecord:
    name: str


class EpicsAdapter(ConfigurableAdapter):
    interrupt_records: Dict[InputRecord, Callable[[], Any]]

    def link_input_on_interrupt(
        self, record: InputRecord, getter: Callable[[], Any]
    ) -> None:
        ...
        self.interrupt_records[record] = getter

    def after_update(self) -> None:
        for record, getter in self.interrupt_records.items():
            current_value = getter()
            record.set(current_value)
            print("Record {} updated to : {}".format(record.name, current_value))

    def build_ioc(self):
        builder.SetDeviceName(self.device_name)

        # From PythonSoftIOC: Load the base records without DTYP fields
        with open(self.db_file, "rb") as inp:
            with NamedTemporaryFile(suffix=".db", delete=False) as out:
                for line in inp.readlines():
                    if not re.match(rb"\s*field\s*\(\s*DTYP", line):
                        out.write(line)

        softioc.dbLoadDatabase(out.name, substitutions=f"device={self.device_name}")
        os.unlink(out.name)

        self.records()

        softioc.devIocStats(self.device_name)

        builder.LoadDatabase()
        event_loop = asyncio.get_event_loop()
        dispatcher = asyncio_dispatcher.AsyncioDispatcher(event_loop)
        softioc.iocInit(dispatcher)
