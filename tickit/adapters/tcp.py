import asyncio
import re
from typing import Callable, List, NewType, Tuple

from tickit.core.adapter import Adapter
from tickit.core.device import Device

Command = NewType("Command", Tuple[str, Callable, bool])


class TcpAdapter(Adapter):
    device: Device
    commands: List[Command] = list()
    interrupt = False

    async def run_forever(self) -> None:
        async def handle(
            reader: asyncio.StreamReader, writer: asyncio.StreamWriter
        ) -> None:
            while True:
                data = await reader.read(1024)
                message = data.decode().strip()
                addr = writer.get_extra_info("peername")

                print("Recieved {} from {}".format(message, addr))
                reply = str.encode(str(await self._handle_message(message)) + "\r\n")
                print("Replying with {!r}".format(reply))
                writer.write(reply)
                await writer.drain()

        server = await asyncio.start_server(handle, "0.0.0.0", 25565)

        async with server:
            await server.serve_forever()

    async def _handle_message(self, message: str) -> str:
        for regex, func, interrupt in self.commands:
            if re.fullmatch(regex, message):
                self.interrupt |= interrupt
                return func(self.device, message)
        return "Request does not match any known command"

    def command(self, command: object, interrupt: bool = False) -> Callable:
        def register(func: Callable) -> Callable:
            self.commands.append(Command((regex, func, interrupt)))
            return func

        try:
            regex: str = str(command)
        except TypeError as e:
            raise e
        return register

    def link(self, device: Device):
        self.device = device
