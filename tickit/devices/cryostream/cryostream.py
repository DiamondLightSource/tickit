import asyncio
import struct
from typing import AsyncIterable, Awaitable, Callable

from tickit.adapters.composed import ComposedAdapter
from tickit.adapters.interpreters.command import CommandInterpreter, RegexCommand
from tickit.adapters.servers.tcp import TcpServer
from tickit.core.adapter import ConfigurableAdapter
from tickit.core.device import ConfigurableDevice, Device, DeviceUpdate
from tickit.core.typedefs import SimTime
from tickit.devices.cryostream.base import CryostreamBase
from tickit.devices.cryostream.states import PhaseIds
from tickit.utils.byte_format import ByteFormat
from tickit.utils.compat.typing_compat import TypedDict

_EXTENDED_STATUS = ">BBHHHBBHHHHHBBBBBBHHBBBBBBBBHH"


class Cryostream(CryostreamBase, ConfigurableDevice):
    Inputs: TypedDict = TypedDict("Inputs", {})
    Outputs: TypedDict = TypedDict("Outputs", {"temperature": float})

    def __init__(self) -> None:
        super().__init__()
        self.phase_id: int = PhaseIds.HOLD.value
        self.callback_period: SimTime = SimTime(int(1e9))

    def update(
        self, time: SimTime, inputs: "Cryostream.Inputs"
    ) -> DeviceUpdate["Cryostream.Outputs"]:
        if self.phase_id in (PhaseIds.RAMP.value, PhaseIds.COOL.value):
            self.gas_temp = self.update_temperature(time)
            return DeviceUpdate(
                Cryostream.Outputs(temperature=self.gas_temp),
                SimTime(time + self.callback_period),
            )
        if self.phase_id == PhaseIds.PLAT.value:
            self.phase_id = PhaseIds.HOLD.value
            return DeviceUpdate(
                Cryostream.Outputs(temperature=self.gas_temp),
                SimTime(time + int(self.plat_duration * 1e10)),
            )
        return DeviceUpdate(Cryostream.Outputs(temperature=self.gas_temp), None)


class CryostreamAdapter(ComposedAdapter, ConfigurableAdapter):
    _device = Cryostream

    def __init__(
        self,
        device: Device,
        raise_interrupt: Callable[[], Awaitable[None]],
        host: str = "localhost",
        port: int = 25565,
    ) -> None:
        super().__init__(
            device,
            raise_interrupt,
            TcpServer(format=ByteFormat(b"%b"), host=host, port=port),
            CommandInterpreter(),
        )

    async def on_connect(self) -> AsyncIterable[bytes]:
        while True:
            await asyncio.sleep(2.0)
            await self._device.set_status_format(1)
            status = await self._device.get_status(1)
            yield status.pack()

    @RegexCommand(b"\\x02\\x0a", interrupt=True)
    async def restart(self) -> None:
        await self._device.restart()

    @RegexCommand(b"\\x02\\x0d", interrupt=True)
    async def hold(self) -> None:
        await self._device.hold()

    @RegexCommand(b"\\x02\\x10", interrupt=True)
    async def purge(self) -> None:
        await self._device.purge()

    @RegexCommand(b"\\x02\\x11", interrupt=True)
    async def pause(self) -> None:
        await self._device.pause()

    @RegexCommand(b"\\x02\\x12", interrupt=True)
    async def resume(self) -> None:
        await self._device.resume()

    @RegexCommand(b"\\x02\\x13", interrupt=True)
    async def stop(self) -> None:
        await self._device.stop()

    @RegexCommand(b"\\x03\\x14([\\x00\\x01])", interrupt=True)
    async def turbo(self, turbo_on: bytes) -> None:
        turbo_on = struct.unpack(">B", turbo_on)[0]
        await self._device.turbo(turbo_on)

    # Todo set status format not interrupt
    @RegexCommand(b"\\x03\\x28([\\x00\\x01])", interrupt=False)
    async def set_status_format(self, status_format: bytes) -> None:
        status_format = struct.unpack(">B", status_format)[0]
        await self._device.set_status_format(status_format)

    @RegexCommand(b"\\x04\\x0c(.{2})", interrupt=True)
    async def plat(self, duration: bytes) -> None:
        duration = struct.unpack(">H", duration)[0]
        await self._device.plat(duration)

    @RegexCommand(b"\\x04\\x0f(.{2})", interrupt=True)
    async def end(self, ramp_rate: bytes) -> None:
        ramp_rate = struct.unpack(">H", ramp_rate)[0]
        await self._device.end(ramp_rate)

    @RegexCommand(b"\\x04\\x0e(.{2})", interrupt=True)
    async def cool(self, target_temp: bytes) -> None:
        target_temp = struct.unpack(">H", target_temp)[0]
        await self._device.cool(target_temp)

    @RegexCommand(b"\\x06\\x0b(.{2,4})", interrupt=True)
    async def ramp(self, values: bytes) -> None:
        ramp_rate, target_temp = struct.unpack(">HH", values)
        await self._device.ramp(ramp_rate, target_temp)
