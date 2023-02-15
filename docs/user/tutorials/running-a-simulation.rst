Running a Simulation
====================

This tutorial shows how to run a tickit simulation both within a single process
and distributed across multiple processes.

Within a Single Process
-----------------------

Tickit simulations may be launched within a single process by executing a command of
the following format ``python -m tickit all [OPTIONS] CONFIG_PATH`` in which ``all``
denotes that both a `MasterScheduler` and the components defined in the config should
be started within the process.

In this tutorial we shall run the sunk trampoline example configuration, located at
``examples/configs/sunk-trampoline.yaml``, as such a simulation may be launched in a
single process by executing the following command:

.. code-block:: bash

    python -m tickit all examples/configs/sunk-trampoline.yaml

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

Across Multiple Processes
-------------------------

In order to run across multiple processes a message broking service must be utilized.
As such, prior to launching any instances of Tickit a message broker must be launched;
In this example we will use apache kafka (the default distributed broker for Tickit),
which may be installed and launched according to steps 1 and 2 of the
`apache kafka quickstart guide <https://kafka.apache.org/quickstart>`_.

Tickit simulations may be launched across multiple processes by executing a command of
the format ``python -m tickit scheduler [OPTIONS] CONFIG_PATH`` to launch a
`MasterScheduler` and commands of the format
``python -m tickit device [OPTIONS] DEVICE CONFIG_PATH`` for each component within the
simulation.


Running a `MasterScheduler` for the sunk trampoline example is performed as:

.. code-block:: bash

    python -m tickit scheduler examples/configs/sunk-trampoline.yaml

Once run, we expect to see an output akin to:

.. code-block:: bash

    Doing tick @ 0
    Topic tickit-rand_tramp-in is not available during auto-create initialization
    Topic tickit-tramp_sink-out is not available during auto-create initialization
    Topic tickit-rand_tramp-out is not available during auto-create initialization

Running the ``rand_tramp`` device for the sunk trampoline example is performed as:

.. code-block:: bash

    python -m tickit device rand_tramp examples/configs/sunk-trampoline.yaml

Once run, we expect to see an output akin to:

.. code-block:: bash

    rand_tramp got Input(target='rand_tramp', time=0, changes=immutables.Map({}))
    Boing! (delta: 0, inputs: immutables.Map({}), output: 162)

With the following being emitted by the `MasterScheduler` process:

.. code-block:: bash

    Scheduler got Output(source='rand_tramp', time=0, changes=immutables.Map({'output': 162}), call_in=1000000000)
    Scheduling Wakeup(component='rand_tramp', when=1000000000)
    Topic tickit-tramp_sink-in is not available during auto-create initialization

Finally we may run the ``tramp_sink`` device for the sunk trampoline example via the
following command:

.. code-block:: bash

    python -m tickit device tramp_sink examples/configs/sunk-trampoline.yaml

Once run, we expect to see an output akin to:

.. code-block:: bash

    tramp_sink got Input(target='tramp_sink', time=0, changes=immutables.Map({'input': 162}))
    Sunk {'input': 162}

With the following being emitted by the `MasterScheduler` process:

.. code-block:: bash

    Scheduler got Output(source='tramp_sink', time=0, changes=immutables.Map({}), call_in=None)

After which the simulation should continue as expected, with relevent information
produced by each of the processes.

.. _MasterScheduler: <tickit.core.management.scheduling.master.MasterScheduler>