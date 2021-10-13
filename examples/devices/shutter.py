from dataclasses import dataclass
from random import random
from typing import Optional

from tickit.adapters.composed import ComposedAdapter
from tickit.adapters.interpreters.command.command_interpreter import CommandInterpreter
from tickit.adapters.interpreters.command.regex_command import RegexCommand
from tickit.adapters.servers.tcp import TcpServer
from tickit.core.components.component import Component, ComponentConfig
from tickit.core.components.device_simulation import DeviceSimulation
from tickit.core.device import Device, DeviceUpdate
from tickit.core.typedefs import SimTime
from tickit.utils.byte_format import ByteFormat
from tickit.utils.compat.typing_compat import TypedDict


class ShutterDevice(Device):
    """A toy device which downscales flux according to a set position.

    A toy device which produces an output flux which is downscaled from the input flux
    according to an internal state position. The position may be altered by setting new
    a target which will be matched by position over a period of time determined by the
    rate.
    """

    #: A typed mapping containing the 'flux' input value
    Inputs: TypedDict = TypedDict("Inputs", {"flux": float})
    #: A typed mapping containing the 'flux' output value
    Outputs: TypedDict = TypedDict("Outputs", {"flux": float})

    def __init__(
        self, default_position: float, initial_position: Optional[float] = None
    ) -> None:
        """A Shutter constructor which configures the initial and default position.

        Args:
            default_position (float): The initial target position of the shutter
            initial_position (Optional[float]): The initial position of the shutter. If
                None, a random value in the range [0.0,1.0) will be used. Defaults to
                None.
        """
        self.target_position = default_position
        self.position = initial_position if initial_position else random()
        self.rate = 2e-10
        self.last_time: Optional[SimTime] = None

    @staticmethod
    def move(position: float, target: float, rate: float, period: SimTime) -> float:
        """A helper method used to compute the new position of a shutter.

        A helper method used to compute the new position of a shutter given a target
        position, a rate of change and a period over which the change occurs. Movement
        is performed at the defined rate and comes to a "hard" stop when the desired
        position is reached.

        Args:
            position (float): The prior position of the shutter.
            target (float): The target position of the shutter.
            rate (float): The rate of change of shutter position.
            period (SimTime): The period over which the change occurs.

        Returns:
            float: The posterior position of the shutter.
        """
        if position < target:
            position = min(position + rate * period, target)
        elif position > target:
            position = max(position - rate * period, target)
        return position

    def update(self, time: SimTime, inputs: Inputs) -> DeviceUpdate[Outputs]:
        """The update method which moves the shutter and produces a downscaled flux.

        The update method which adjusts the position according to the target position,
        computes the transmitted flux and produces the output flux with a request to be
        called back in 100ms if the if the shutter continues to move.

        Args:
            time (SimTime): The current simulation time (in nanoseconds).
            inputs (State): A mapping of inputs to the device and their values.

        Returns:
            DeviceUpdate[Outputs]:
                The produced update event which contains the value of the transmitted
                flux, and requests a callback after 100ms if the shutter continues to
                move.
        """
        if self.last_time:
            self.position = self.move(
                self.position,
                self.target_position,
                self.rate,
                SimTime(time - self.last_time),
            )
        self.last_time = time
        call_at = (
            None if self.position == self.target_position else SimTime(time + int(1e8))
        )
        output_flux = inputs["flux"] * self.position
        return DeviceUpdate(self.Outputs(flux=output_flux), call_at)


class ShutterAdapter(ComposedAdapter):
    """A toy composed adapter which gets shutter position and target and sets target."""

    device: ShutterDevice

    def __init__(
        self,
        host: str = "localhost",
        port: int = 25565,
    ) -> None:
        """A Shutter which instantiates a TcpServer with configured host and port.

        Args:
            device (Device): The device which this adapter is attached to
            raise_interrupt (Callable): A callback to request that the device is
                updated immediately.
            host (Optional[str]): The host address of the TcpServer. Defaults to
                "localhost".
            port (Optional[int]): The bound port of the TcpServer. Defaults to 25565.
        """
        super().__init__(
            TcpServer(host, port, ByteFormat(b"%b\r\n")),
            CommandInterpreter(),
        )

    @RegexCommand(r"P\?", False, "utf-8")
    async def get_position(self) -> bytes:
        """A regex string command which returns the utf-8 encoded value of position.

        Returns:
            bytes: The utf-8 encoded value of position.
        """
        return str(self.device.position).encode("utf-8")

    @RegexCommand(r"T\?", False, "utf-8")
    async def get_target(self) -> bytes:
        """A regex string command which returns the utf-8 encoded value of target.

        Returns:
            bytes: The utf-8 encoded value of target.
        """
        return str(self.device.target_position).encode("utf-8")

    @RegexCommand(r"T=(\d+\.?\d*)", True, "utf-8")
    async def set_target(self, target: str) -> None:
        """A regex string command which sets the target position of the shutter.

        Args:
            target (str): The target position of the shutter.
        """
        self.device.target_position = float(target)
        self.device.last_time = None


@dataclass
class Shutter(ComponentConfig):
    """Shutter you can open or close over TCP."""

    default_position: float
    initial_position: Optional[float] = None
    host: str = "localhost"
    port: int = 25565

    def __call__(self) -> Component:  # noqa: D102
        return DeviceSimulation(
            name=self.name,
            device=ShutterDevice(
                default_position=self.default_position,
                initial_position=self.initial_position,
            ),
            adapters=[ShutterAdapter(host=self.host, port=self.port)],
        )
