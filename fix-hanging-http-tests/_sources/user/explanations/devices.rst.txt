Devices
=======

Tickit simulations revolve around devices. Devices are user implemented classes
with behaviour that mimics the hardware you wish to simulate.

Any new device created must extend `Device`, have an update method, and must
have Input and Output maps as members. If these are not used they can be left
empty, but they must be present. This is for the wiring together of multiple
devices within a simulation. :doc:`Further details on wiring.<wiring>`

The following code is for a ``RandomTrampoline``. This device just outputs random
values and requests to be called back for an update sometime later.

.. code-block:: python

    class RandomTrampolineDevice(Device):
    """A trivial toy device which produced a random output and requests a callback."""

        #: An empty typed mapping of device inputs
        class Inputs(TypedDict):
            ...
        #: A typed mapping containing the 'output' output value
        class Outputs(TypedDict):
            output: int

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
                f"Boing! (delta: {time}, inputs: {inputs}, output: {output})"
            )
            return DeviceUpdate(
                RandomTrampolineDevice.Outputs(output=output),
                SimTime(time + self.callback_period),
            )


Logic can be implemented into the device via device methods. For an example of
this look at the ``ShutterDevice``. It acts to attenuate the flux of any incoming
value.
