from tickit.adapters.composed import ComposedAdapter
from tickit.adapters.interpreters.command.regex_command import RegexCommand
from tickit.core.components.system_simulation_view import SystemSimulationView


class ZebraAdapter(ComposedAdapter[bytes, SystemSimulationView]):
    """network adapetr for zebra system simulation"""

    _device: SystemSimulationView

    _registry: dict

    # has registry, [dictionary]
    # a single adress/register of the registry is mapped to a single attribute of a
    # device

    # do logic for set and get registers to map to correct device attributes

    @RegexCommand(rb"W([0-9A-F]{2})([0-9A-F]{4})\n", interrupt=True)
    async def set_reg(self, addr: str, value: str) -> bytes:
        # addr_int, value_int = int(addr, base=16), int(value, base=16)
        # set thing
        return

    @RegexCommand(rb"R([0-9A-F]{2})\n")
    async def get_reg(self, addr: str) -> bytes:
        # addr_int = int(addr, base=16)
        # get thing
        return
