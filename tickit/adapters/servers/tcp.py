import asyncio
from dataclasses import dataclass
from typing import Awaitable, Callable

from tickit.core.adapter import ServerConfig


@dataclass
class TcpServerConfig(ServerConfig):
    server_class = "tickit.adapters.servers.tcp.TcpServer"
    host: str
    port: int


class TcpServer:
    def __init__(self, config: TcpServerConfig) -> None:
        self.host = config.host
        self.port = config.port

    async def run_forever(self, handler: Callable[[bytes], Awaitable[bytes]]) -> None:
        async def handle(
            reader: asyncio.StreamReader, writer: asyncio.StreamWriter
        ) -> None:
            while True:
                data: bytes = await reader.read(1024)
                if data == b"":
                    break
                addr = writer.get_extra_info("peername")

                print("Recieved {!r} from {}".format(data, addr))
                reply = str.encode(str(await handler(data)) + "\r\n")
                print("Replying with {!r}".format(reply))
                writer.write(reply)
                await writer.drain()

        server = await asyncio.start_server(handle, self.host, self.port)

        async with server:
            await server.serve_forever()
