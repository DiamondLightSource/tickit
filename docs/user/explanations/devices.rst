Devices
=======

Tickit simulations revolve around devices. Devices are user implemented classes
which behaviours mimic the hardware you wish to simulate.

Any new device created must be of type device, have an `update` method, and must
have Input and Output maps as members. If these are not used they can be left
empty, but they must be present. This is for the wiring together of multiple
devices within a simulation. :doc:`Further details on wiring <wiring>`.

The following code is for a `RandomTrampoline`. This device just outputs random
values and requests to be called back for an update sometime later.

.. code-block:: python

    class RandomTrampolineDevice(Device):
    """A trivial toy device which produced a random output and requests a callback."""

    #: An empty typed mapping of device inputs
    Inputs: TypedDict = TypedDict("Inputs", {})
    #: A typed mapping containing the 'output' output value
    Outputs: TypedDict = TypedDict("Outputs", {"output": int})

    def __init__(self, callback_period: int = int(1e9)) -> None:
        self.callback_period = SimTime(callback_period)

    def update(self, time: SimTime, inputs: Inputs) -> DeviceUpdate[Outputs]:
        """The update method which produces a random output and requests a callback.

        Returns:
            DeviceUpdate[Outputs]:
                The produced update event which contains the value of the random output,
                and requests a callback after the configured callback period.
        """
        output = randint(0, 255)
        LOGGER.debug(
            "Boing! (delta: {}, inputs: {}, output: {})".format(time, inputs, output)
        )
        return DeviceUpdate(
            RandomTrampolineDevice.Outputs(output=output),
            SimTime(time + self.callback_period),
        )

For a device that does something more useful, here is a simulated shutter. It
acts to attenuate the flux of any incoming beam:

.. code-block:: python

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