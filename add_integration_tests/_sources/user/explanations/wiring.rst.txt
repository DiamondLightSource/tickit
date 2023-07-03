Wiring
======

As an event-based multi-device simulation framework, tickit has the capability
to contain multiple devices in one simulation. These devices can be wired
together to create more complex and intricate systems.

The devices in a simulation can be wired together, with the output of one device
wired to the input of another. This ensures devices update in the correct order,
so that changes in the system propgate in the correct manner. This is structured
as a directed acyclic graph.

.. figure:: ../../images/tickit-simple-dag.svg
    :align: center

Here we can see that if component 1 updates, then this will cause component 2
to update, which in turn causes 4 to update. Component 4 will not update untill
component 3 has also updated, as component 4 depends on both component 2 and 3.

This wiring is achieved with a configuration yaml file which is passed to the
scheduler when starting a simulation. Here we see an example trampoline device
which outputs random numbers, and a sink taking that output as an input:

.. code-block:: yaml

    - examples.devices.trampoline.RandomTrampoline:
        name: rand_tramp
        inputs: {}
        callback_period: 1000000000
    - tickit.devices.sink.Sink:
        name: tramp_sink
        inputs:
          input: rand_tramp:output
