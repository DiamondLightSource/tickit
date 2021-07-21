import asyncio
from typing import Awaitable, Callable


class TcpServer:
    async def run_forever(self, handler: Callable[[str], Awaitable[str]]) -> None:
        async def handle(
            reader: asyncio.StreamReader, writer: asyncio.StreamWriter
        ) -> None:
            while True:
                data: bytes = await reader.read(1024)
                message: str = data.decode().strip()
                addr = writer.get_extra_info("peername")

                print("Recieved {} from {}".format(message, addr))
                reply = str.encode(str(await handler(message)) + "\r\n")
                print("Replying with {!r}".format(reply))
                writer.write(reply)
                await writer.drain()

        server = await asyncio.start_server(handle, "0.0.0.0", 25565)

        async with server:
            await server.serve_forever()
