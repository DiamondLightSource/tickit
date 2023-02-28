Creating a Simulation
=====================

This tutorial shows how to create a simulated system consisting of several included
devices using the tickit framework - specifically a ``RandomTrampoline`` and a `Sink`.

Configuration File
------------------

We shall begin by creating a new YAML file named ``my_simulation.yaml``, and open it
with our preferred text editor. This file will be used to configure each of the devices
and wire them together.

Adding Devices
--------------

In order to be included in a simulation, tickit devices must have a `ComponentConfig`
dataclass associated with them. This defines the device to be used, as well as any
adapters to allow the device to be externally controlled. At the top level, tickit 
simulations comprise a list of these components which are denoted in YAML.

In this example our first device shall be a ``RandomTrampoline`` with a callback_period 
of :math:`1s` or :math:`10^9n\s` named ``rand_tramp`` with no adapters - denoted 
in YAML by ``[]`` - and with no mapped inputs - denoted in YAML by ``{}``. As such 
we may extend our config, as:

.. code-block:: yaml
    
    - examples.devices.trampoline.RandomTrampoline:
        name: rand_tramp
        inputs: {}

We will now add a `Sink` device. This device will be named ``tramp_sink``, will have 
no adapters but will take the ``output`` value of ``rand_tramp`` as ``input``. As 
such we may extend our config, as:

.. code-block:: yaml
    
    - examples.devices.trampoline.RandomTrampoline:
        name: rand_tramp
        inputs: {}
    - tickit.devices.sink.Sink:
        name: tramp_sink        
        inputs:
          input:
          - rand_tramp:output

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

.. seealso:: 
    :doc:`Running a Simulation<running-a-simulation>`

.. _Sink: <tickit.devices.sink.Sink>
