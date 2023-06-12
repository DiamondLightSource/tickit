Create a Device with an EPICS Interface
=======================================

It is possible to make a device accessable over channel access with EPICS by
using an EPICS adapter with the device.

.. note::
    For information on EPICS, see `here. <https://epics.anl.gov/>`_

This adapter creates and runs a python soft IOC within the simulator process. The
PV's on this IOC can be accessed with the normal methods, eg ``caget``, ``caput`` etc.

If you have multiple devices in your simulation that require an epics adapter
this is possible, a large singleton IOC is created as a composite IOC of all the
individual ones.

Using an EPICS adapter
-----------------------

When you create an IOC you often will have a db file, depicting the PVs that
should be present on it. The epics adapter allows for loading of these PVs from
the DB file so that you do not have to populate them by hand. This file is
loaded into the adapter when the component is initialised. For example the Femto
component:

.. code-block:: python

    @dataclass
    class Femto(ComponentConfig):
        """Femto simulation with EPICS IOC."""

        initial_gain: float = 2.5
        initial_current: float = 0.0
        db_file: str = "path/to/record.db"
        ioc_name: str = "FEMTO"

        def __call__(self) -> Component:  # noqa: D102
            return DeviceSimulation(
                name=self.name,
                device=FemtoDevice(
                    initial_gain=self.initial_gain, initial_current=self.initial_current
                ),
                adapters=[FemtoAdapter(db_file=self.db_file, ioc_name=self.ioc_name)],
            )


However, any PV you wish to directly link to a device attribute you must override
and provide the neccessary methods to get and set that attribute.

See again the femto device. It is a signal amplifier that takes an input and
outputs a current.

.. code-block:: python

    class FemtoDevice(Device):
        """Electronic signal amplifier."""

        Inputs: TypedDict = TypedDict("Inputs", {"input": float})
        Outputs: TypedDict = TypedDict("Outputs", {"current": float})

        def __init__(
            self,
            initial_gain: float,
            initial_current: float,
        ) -> None:
            self.gain: float = initial_gain
            self._current: float = initial_current

        def set_gain(self, gain: float) -> None:
            self.gain = gain

        def get_gain(self) -> float:
            return self.gain

        def set_current(self, input_current: float) -> None:
            self._output_current = input_current * self.gain

        def get_current(self) -> float:
            return self._output_current

        def update(self, time: SimTime, inputs: Inputs) -> DeviceUpdate[Outputs]:
            current_value = inputs["input"]
            if current_value is not None:
                self.set_current(current_value)
            return DeviceUpdate(self.Outputs(current=self.get_current()), None)


The femto device has a PV GAIN as an ``ao`` record (analogue out).

.. code-block:: C
    
    record(ao, "$(device):GAIN") {
      field(DTYP, "Hy8001")
      field(OMSL, "supervisory")
      field(OUT, "#C1 S0 @")
      field(DESC, "Gain value")
      field(EGU, "A")
    }

This means it is settable by the user, you should be able to ``caput`` a gain
value to change the PV. In order to get the device to update its attribute ``gain``
to reflect that, we must override the epics adapter function ``on_db_load``.

.. code-block:: python

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


We provide a callback function to set the device gain to the new value then
raise an interrupt, causing the device to update. This callback function is
assigned to the epics record ``GAIN`` so that a change in that changes the device.
A similar linking proccess occurs for readable records, eg ``aIn``, however these
are just supplied with getter methods to the device attributes.

As a result the Femto device is accessable via EPICS. It gain can be set, and
its gain and current read via the IOC.