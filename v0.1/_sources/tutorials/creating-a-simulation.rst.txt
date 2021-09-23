Creating a Simulation
=====================

This tutorial shows how to create a simulated system consisting of several included
devices using the tickit framework - specifically a `RandomTrampoline` and a `Sink`.

Configuration File
------------------

We shall begin by creating a new YAML file named ``my_simulation.yaml``, and open it
with our preferred text editor. This file will be used to configure each of the devices
and wire them together.

Adding Devices
--------------

In order to be included in a simulation, tickit devices must be nested within a
`DeviceSimulation` component. At the top level, tickit simulations comprise a list of
components - denoted in YAML by ``-``. As such we shall begin by adding an empty
`DeviceSimulation` as the first element of our list, as:

.. code-block:: yaml
    
    - tickit.core.components.device_simulation.DeviceSimulation:

A `DeviceSimulation` wraps a device and a set of adapters, giving them a name and
mapping the device inputs to the outputs of other devices. In this example our first
device shall be a `RandomTrampoline` with a callback_period of :math:`1s` or
:math:`10^9\mu\\s` named ``rand_tramp`` with no adapters - denoted in YAML by ``[]`` -
and with no mapped inputs - denoted in YAML by ``{}``. As such we may extend our
config, as:

.. code-block:: yaml
    
    - tickit.core.components.device_simulation.DeviceSimulation:
        adapters: []
        device:
          examples.devices.trampoline.RandomTrampoline:
            callback_period: 1000000000
        inputs: {}
        name: rand_tramp

We will now add a `Sink` device, again wrapped within a `DeviceSimulation`. This device
will be named ``tramp_sink``, will have no adapters but will take the ``output`` value
of ``rand_tramp`` as ``input``. As such we may extend our config, as:

.. code-block:: yaml
    
    - tickit.core.components.device_simulation.DeviceSimulation:
        adapters: []
        device:
          examples.devices.trampoline.RandomTrampoline:
            callback_period: 1000000000
        inputs: {}
        name: rand_tramp
    - tickit.core.components.device_simulation.DeviceSimulation:
        adapters: []
        config:
          tickit.devices.sink.Sink: {}
        inputs:
          input:
          - rand_tramp:output
        name: tramp_sink

Running the Simulation
----------------------

Finally, we likely wish to run the simulation, this may be performed by running the
following command:

.. code-block:: bash

    python -m tickit all my_simulation.yaml

Once run, we expect to see an output akin to:

.. code-block:: bash

    Doing tick @ 0
    rand_tramp got Input(target='rand_tramp', time=0, changes=immutables.Map({}))
    Boing! (delta: 0, inputs: immutables.Map({}), output: 225)
    Scheduler got Output(source='rand_tramp', time=0, changes=immutables.Map({'output': 225}), call_in=1000000000)
    Scheduling Wakeup(component='rand_tramp', when=1000000000)
    tramp_sink got Input(target='tramp_sink', time=0, changes=immutables.Map({'input': 225}))
    Sunk {'input': 225}
    Scheduler got Output(source='tramp_sink', time=0, changes=immutables.Map({}), call_in=None)
    Doing tick @ 1000000000
    rand_tramp got Input(target='rand_tramp', time=1000000000, changes=immutables.Map({}))
    Boing! (delta: 1000000000, inputs: immutables.Map({}), output: 139)
    Scheduler got Output(source='rand_tramp', time=1000000000, changes=immutables.Map({'output': 139}), call_in=1000000000)
    Scheduling Wakeup(component='rand_tramp', when=2000000000)
    tramp_sink got Input(target='tramp_sink', time=1000000000, changes=immutables.Map({'input': 139}))
    Sunk {'input': 139}
    Scheduler got Output(source='tramp_sink', time=1000000000, changes=immutables.Map({}), call_in=None)

.. seealso:: `Running a Simulation`

.. _Sink: <tickit.devices.sink.Sink>
.. _RandomTrampoline:  <examples.devices.trampoline.RandomTrampoline>
.. _DeviceSimulation: <tickit.core.components.device_simulation.DeviceSimulation>