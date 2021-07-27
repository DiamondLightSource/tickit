import asyncio
from asyncio.streams import StreamReader, StreamWriter
from dataclasses import dataclass
from typing import AsyncIterable, Awaitable, Callable, List

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

    async def run_forever(
        self,
        on_connect: Callable[[], AsyncIterable[bytes]],
        handler: Callable[[bytes], Awaitable[AsyncIterable[bytes]]],
    ) -> None:
        tasks: List[asyncio.Task] = list()

        async def handle(reader: StreamReader, writer: StreamWriter) -> None:
            async def reply(reply: AsyncIterable[bytes]) -> None:
                async for rep in reply:
                    if rep is None:
                        continue
                    print("Replying with {!r}".format(rep))
                    writer.write(rep + b"\n\r")
                    if writer.is_closing():
                        break
                    await writer.drain()

            tasks.append(asyncio.create_task(reply(on_connect())))

            while True:
                data: bytes = await reader.read(1024)
                if data == b"":
                    break
                addr = writer.get_extra_info("peername")

                print("Recieved {!r} from {}".format(data, addr))
                tasks.append(asyncio.create_task(reply(await handler(data))))

            await asyncio.wait(tasks)

        server = await asyncio.start_server(handle, self.host, self.port)

        async with server:
            await server.serve_forever()
