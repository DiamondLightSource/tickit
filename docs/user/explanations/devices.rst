Devices
=======

Tickit simulations revolve around devices. Devices are user implemented classes
which behaviours mimic the hardware you wish to simulate.

Any new device created must be of type device, have an update method, and must
have Input and Output maps as members. If these are not used they can be left
empty, but they must be present. This is for the wiring together of multiple
devices within a simulation. :doc: `Further details on wiring <wiring>`_

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

For a more involved device look at the `ShutterDevice`. It acts to attenuate the
flux of any incoming value.

.. _RandomTrampoline:  <examples.devices.trampoline.RandomTrampoline>
.. _ShutterDevice: <examples.devices.shutter.ShutterDevice>