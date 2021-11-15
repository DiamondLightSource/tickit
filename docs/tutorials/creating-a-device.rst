Creating a Device
=================

This tutorial shows how to create a simple `Device` for use in the tickit framework.
This device will act as a simple shutter which can vary the transmission of ``flux`` by
changing ``position``.

Device Module File
------------------

We shall begin by creating a new python module named ``my_shutter.py``, and open it
with our preferred editor. This file will be used to store the our Shutter class which
will determine the operation of our device.

Device Class
------------

We shall begin by defining the Shutter class which inherits `Device` - by
doing so a confiuration dataclass will automatically be created for the device,
allowing for easy YAML configuration.

.. code-block:: python

    from tickit.core.device import Device


    class ShutterDevice(Device):

Device Constructor and Configuration
------------------------------------

Next, we shall create the ``__init__`` method, allowing for the device to be
instantiated. We will pass two arguments to this method; a required argument,
``default_position``, which will specify the ``target_position`` of the shutter in the
absence of any other instruction; and an optional argument, ``initial_position``,
which when specified will set the initial ``position`` of the shutter, if unspecified
the initial ``position`` will be random.

.. code-block:: python

    from random import random
    from typing import Optional

    from tickit.core.device import Device


    class ShutterDevice(Device):
        def __init__(
            self, default_position: float, initial_position: Optional[float] = None
        ) -> None:
            self.target_position = default_position
            self.position = initial_position if initial_position else random()

.. note::
    Arguments to the ``__init__`` method may be specified in the simulation config file
    if the device inherits `Device`.

Device Logic
------------

The core logic of the device will be implemented in the ``update`` method which
recieves the arguments ``time`` - the current simulation time in nanoseconds - and
``inputs`` - a mapping of input ports to their value - and returns an `DeviceUpdate`
which consists of ``outputs`` - a mapping of output ports and their value - and
``call_at`` - the time at which the device should next be updated.

.. code-block:: python

    from random import random
    from typing import Optional
    from typing_extensions import TypedDict

    from tickit.core.device import Device, DeviceUpdate
    from tickit.core.typedefs import SimTime


    class ShutterDevice(Device):
        Inputs = TypedDict("Inputs", {"flux": float})
        Outputs = TypedDict("Outputs", {"flux": float})

        def __init__(
            self, default_position: float, initial_position: Optional[float] = None
        ) -> None:
            self.target_position = default_position
            self.position = initial_position if initial_position else random()
            self.rate = 2e-10
            self.last_time: Optional[SimTime] = None

        @staticmethod
        def move(position: float, target: float, rate: float, period: SimTime) -> float:
            if position < target:
                position = min(position + rate * period, target)
            elif position > target:
                position = max(position - rate * period, target)
            return position

        def update(self, time: SimTime, inputs: Inputs) -> DeviceUpdate[Outputs]:
            if self.last_time:
                self.position = Shutter.move(
                    self.position,
                    self.target_position,
                    self.rate,
                    SimTime(time - self.last_time),
                )
            self.last_time = time
            call_at = None if self.position == self.target_position else SimTime(time + int(1e8))
            output_flux = inputs["flux"] * self.position
            return DeviceUpdate(Shutter.Outputs(flux=output_flux), call_at)

Creating a ComponentConfig
--------------------------

In order to run the Device as a simulation, it requires a `ComponentConfig` that 
knows how to instantiate that Device. This will be defined in the same file as the
device, and defines any default initial configuration values. As well as this, we
overwrite the magic method `__call__()`, which returns a `DeviceSimulation` object.
This object takes the component name, as well as it's device. We will return to this
if the device requires any adapters to control it externally (see `Creating an Adapter`).

.. code-block:: python

    from tickit.core.components.component import Component, ComponentConfig
    from tickit.core.components.device_simulation import DeviceSimulation


    @dataclass
    class Shutter(ComponentConfig):
        default_position: float
        initial_position: Optional[float] = None

        def __call__(self) -> Component:
            return DeviceSimulation(
                name=self.name,
                device=ShutterDevice(
                    default_position=self.default_position,
                    initial_position=self.initial_position,
                ),
            )


Using the Device
----------------

In order to use the device we must first create a simulation configuration file, we
shall create one named ``my_shutter_simulation.yaml``, and open it with our preferred
editor. This file will be used to set up a simulation consisting of a `Source` named
source which will produce a constant flux, the shutter which will act on the flux as
per our implementation, and a `Sink` named sink which will recieve the resulting flux.

.. code-block:: yaml

    - tickit.devices.source.Source:
        name: source
        inputs: {}
        value: 42.0
    - examples.devices.shutter.Shutter:
        name: shutter
        inputs:
          flux: source:value
        default_position: 0.2
        initial_position: 0.24
    - tickit.devices.sink.Sink:
        name: sink
        inputs:
        flux: shutter:flux

.. seealso::
    See the `Creating a Simulation` tutorial for a walk-through of creating simulation
    configurations.

Finally, we likely wish to run the simulation, this may be performed by running the
following command:

.. code-block:: bash

    python -m tickit all my_shutter_simulation.yaml

Once run, we expect to see an output akin to:

.. code-block:: bash

    Doing tick @ 0
    source got Input(target='source', time=0, changes=immutables.Map({}))
    Sourced 42.0
    Scheduler got Output(source='source', time=0, changes=immutables.Map({'value': 42.0}), call_in=None)
    shutter got Input(target='shutter', time=0, changes=immutables.Map({'flux': 42.0}))
    Scheduler got Output(source='shutter', time=0, changes=immutables.Map({'flux': 10.08}), call_in=100000000)
    Scheduling Wakeup(component='shutter', when=100000000)
    sink got Input(target='sink', time=0, changes=immutables.Map({'flux': 10.08}))
    Sunk {'flux': 10.08}
    Scheduler got Output(source='sink', time=0, changes=immutables.Map({}), call_in=None)
    Doing tick @ 100000000
    shutter got Input(target='shutter', time=100000000, changes=immutables.Map({}))
    Scheduler got Output(source='shutter', time=100000000, changes=immutables.Map({}), call_in=100000000)
    Scheduling Wakeup(component='shutter', when=200000000)
    sink got Input(target='sink', time=100000000, changes=immutables.Map({}))
    Sunk {'flux': 10.08}
    Scheduler got Output(source='sink', time=100000000, changes=immutables.Map({}), call_in=None)
    Doing tick @ 200000000
    shutter got Input(target='shutter', time=200000000, changes=immutables.Map({}))
    Scheduler got Output(source='shutter', time=200000000, changes=immutables.Map({'flux': 9.24}), call_in=100000000)
    Scheduling Wakeup(component='shutter', when=300000000)
    sink got Input(target='sink', time=200000000, changes=immutables.Map({'flux': 9.24}))
    Sunk {'flux': 9.24}
    Scheduler got Output(source='sink', time=200000000, changes=immutables.Map({}), call_in=None)
    Doing tick @ 300000000
    shutter got Input(target='shutter', time=300000000, changes=immutables.Map({}))
    Scheduler got Output(source='shutter', time=300000000, changes=immutables.Map({'flux': 8.4}), call_in=None)
    sink got Input(target='sink', time=300000000, changes=immutables.Map({'flux': 8.4}))
    Sunk {'flux': 8.4}
    Scheduler got Output(source='sink', time=300000000, changes=immutables.Map({}), call_in=None)

.. seealso::
    See the `Running a Simulation` tutorial for a walk-through of running a simulation
    in a single or across multiple processes.