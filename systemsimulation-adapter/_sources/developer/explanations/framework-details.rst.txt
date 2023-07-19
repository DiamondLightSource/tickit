Framework Details
=================

Tickit is an event-based simulation framework allowing for the simulation of
complex multi-device systems.

A tickit simulation consists of a scheduler and components, all of which
communicate via a message bus.

.. figure:: ../../images/tickit-overview-full.svg
    :align: center


On start up the config.yaml file is serialised to provide the wiring used by the
scheduler. This wiring is a map of the unique ids of components in the system to
the inputs the components take. This provides graphs like the one below for
update flow through the system.

.. figure:: ../../images/tickit-simple-dag.svg
    :align: center


The scheduler
-------------

The main parts of the scheduler are the state consumer and producer, and the
ticker.

State Consumer and producer
+++++++++++++++++++++++++++

The consumer and producer are for the messaging between the scheduler and
the system components via the message bus. This is organised with topics that
messages can be published to and that consumers can be subscribed to in order to
receive those messages. The scheduler sets up the consumer to handle messages
in a given way and subscribes itself to the output topic of every component
in the system.

Whenever a device produces a device update, the scheduler consumes that output
and propagates it to the relevant inputs via the ticker.

The ticker
++++++++++

The ticker contains the logic for the propagation of an update through the system.



One update cycle
----------------

When the simulation starts it initialises all of the components and runs through
its first tick.


The scheduler contains a list of wakeups, which is a dictionary of component ids
and simtimes of when that component wants calling back.

(these wakeups are the callbacks requested with the `DeviceUpdate` returned when
you run a device update.)

If there are no scheduled wakeups then the system will wait until a new wake up
is created. This is done via an interrupt. These can be caused by an adapter
changing something on a device. In this case an immediate wake up is scheduled
for the device the adapter is connected to.

When we have a scheduled wakeups the scheduler will check its dictionary of wakeups
to find the shortest time to the next wakeup and will then find the set of
components which requested a wakeup at that time. This will often only be one component
but could be multiple.

We then wait for one of two events to occur. Either the time until the wake up
elapses, or we are interrupted in that time by an immediate wakeup.

Lets say we are not interrupted and the scheduled wakeup occurs.

The ticker is then called for that time, with each component in the set in turn.
one call of the ticker will begin a tick at that time, update the component,
wait for the scheduler to receive back an output and use that to acknowledge the
component has updated, produce the input in the correct channel, then get the
next component in the graph to update. This propagates until the last component
has updated and it passed back to the scheduler.

The real time is then stored and we go back to looking for the next wakeup.

Each tick as far as the simulation is concerned is instantaneous, therefore over
time we can expect sim time to lag real time. This is mostly negligible but
could potentially cause issues in larger more complex systems.




What is actually running_forever?
---------------------------------

There are run forever methods for all the adapters in a system and in the master
scheduler. These are the basis of the runner tasks. The adapters are waiting for
incoming messages and the scheduler run forever is running system ticks based on
updates.
