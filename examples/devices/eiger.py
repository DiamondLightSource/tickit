from random import random
from typing import Awaitable, Callable, Optional

from tickit.adapters.composed import ComposedAdapter
from tickit.adapters.interpreters.command.command_interpreter import CommandInterpreter
from tickit.adapters.interpreters.command.regex_command import RegexCommand
from tickit.adapters.servers.http import HttpServer
from tickit.core.adapter import ConfigurableAdapter, ConfigurableServer
from tickit.core.device import ConfigurableDevice, DeviceUpdate
from tickit.core.typedefs import Input, Output, SimTime
from tickit.utils.byte_format import ByteFormat
from tickit.utils.compat.typing_compat import TypedDict


class Eiger(ConfigurableDevice):

    Inputs: TypedDict = TypedDict("Inputs", {"trigger": bool})

    Outputs: TypedDict = TypedDict("Outputs", {"Current": float})

    def __init__(
        self,
        trigger: bool = False,
        num_images: Optional[int] = 3600,
        block_size: Optional[int] = 1000,
    ) -> None:
        """[summary]

        Args:
            num_images (int, optional): [description]. Defaults to 3600.
            block_size (int, optional): [description]. Defaults to 1000.
        """

        self.trigger = trigger
        self.num_images = num_images
        self.block_size = block_size

    def update(self, time: SimTime, inputs: Inputs) -> DeviceUpdate[Outputs]:
        pass


class EigerAdapter(ComposedAdapter, ConfigurableAdapter):

    _device: Eiger

    def __init__(
        self,
        device: Eiger,
        raise_interrupt: Callable[[], Awaitable[None]],
        host: str = "localhost",
        port: int = 8080,
    ) -> None:

        super().__init__(
            device,
            raise_interrupt,
            HttpServer(host, port, ByteFormat(b"%b\r\n")),
            CommandInterpreter(),
        )
