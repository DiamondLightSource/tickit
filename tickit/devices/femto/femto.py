from random import uniform

from softioc import builder

from tickit.adapters.epicsadapter import EpicsAdapter
from tickit.core.device import Device, DeviceUpdate
from tickit.core.typedefs import SimTime
from tickit.utils.compat.typing_compat import TypedDict


class FemtoDevice(Device):
    """Electronic signal amplifier."""

    Outputs: TypedDict = TypedDict("Outputs", {"current": float})

    def __init__(
        self,
        initial_gain: float,
        initial_current: float,
    ) -> None:
        """Initialise the Femto device class.

        Args:
            initial_gain (Optional[float]): The initial amplified difference between \
                the input and output signals. Defaults to 2.5.
            initial_current (Optional[float]): The input signal current. \
                Defaults to 0.0.
        """
        self.gain: float = initial_gain
        self._current: float = initial_current

    def set_gain(self, gain: float) -> None:
        """Sets a new amplified difference between the input and output signals.

        Args:
            gain (float): The amplified difference between the input and output signals.
        """
        self.gain = gain

    def get_gain(self) -> float:
        """Returns the current amplified difference between the input and output signals.

        Returns:
            float: the amplified difference between the input and output signals.
        """
        return self.gain

    def set_current(self, input_current: float) -> None:
        """Set the output current based on the input current and the gain.

        The output current is calculated as:
            output_current = input_current * gain

        Args:
            input_current (float): The current of the input signal.
        """
        self._output_current = input_current * self.gain

    def get_current(self) -> float:
        """Returns the output current of the signal.

        Returns:
            float: The output current of the signal.
        """
        return self._output_current

    def update(self, time: SimTime, inputs: dict) -> DeviceUpdate:
        """Updates the state of the Femto device.

        Args:
            time (SimTime): The time of the simulation in nanoseconds.
            inputs (dict): The dict containing the input values of gain and current.

        Returns:
            DeviceUpdate: A container for the Device's outputs and a callback time.
        """
        current_value = inputs.get("input", None)
        if current_value is not None:
            self.set_current(current_value)

        return DeviceUpdate(self.Output(current=self.get_current()), None)


class CurrentDevice(Device):
    """The current configured device."""

    Outputs: TypedDict = TypedDict("Outputs", {"output": float})

    def __init__(self, callback_period: int) -> None:
        """Initialise the current device.

        Args:
            callback_period (Optional[int]): The duration in which the device should \
                next be updated. Defaults to int(1e9).
        """
        self.callback_period = SimTime(callback_period)

    def update(self, time: SimTime, inputs) -> DeviceUpdate[Outputs]:
        """Updates the state of the current device.

        Args:
            time (SimTime): The time of the simulation in nanoseconds.
            inputs (State): The state of the input values of the device.

        Returns:
            DeviceUpdate: A container for the Device's outputs and a callback time.
        """
        output = uniform(0.1, 200.1)
        print(
            "Output! (delta: {}, inputs: {}, output: {})".format(time, inputs, output)
        )
        return DeviceUpdate(
            self.Outputs(output=output), SimTime(time + self.callback_period)
        )


class FemtoAdapter(EpicsAdapter):
    """The adapter for the Femto device."""

    device: FemtoDevice

    async def callback(self, value) -> None:
        """Device callback function.

        Args:
            value (float): The value to set the gain to.
        """
        self.device.set_gain(value)
        await self.raise_interrupt()

    def on_db_load(self) -> None:
        """Customises records that have been loaded in to suit the simulation."""
        builder.aOut(
            "GAIN", initial_value=self.device.get_gain(), on_update=self.callback
        )
        self.link_input_on_interrupt(builder.aIn("GAIN_RBV"), self.device.get_gain)
        self.link_input_on_interrupt(builder.aIn("CURRENT"), self.device.get_current)
