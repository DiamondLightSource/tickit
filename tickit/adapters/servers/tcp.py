import asyncio
from asyncio.streams import StreamReader, StreamWriter
from typing import AsyncIterable, Awaitable, Callable, List

from tickit.core.adapter import ConfigurableServer
from tickit.utils.byte_format import ByteFormat


class TcpServer(ConfigurableServer):
    def __init__(
        self,
        host: str = "localhost",
        port: int = 25565,
        format: ByteFormat = ByteFormat(b"%b"),
    ) -> None:
        self.host = host
        self.port = port
        self.format = format.format

    async def run_forever(
        self,
        on_connect: Callable[[], AsyncIterable[bytes]],
        handler: Callable[[bytes], Awaitable[AsyncIterable[bytes]]],
    ) -> None:
        tasks: List[asyncio.Task] = list()

        async def handle(reader: StreamReader, writer: StreamWriter) -> None:
            async def reply(replies: AsyncIterable[bytes]) -> None:
                async for reply in replies:
                    if reply is None:
                        continue
                    print("Replying with {!r}".format(reply))
                    writer.write(self.format % reply)
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
