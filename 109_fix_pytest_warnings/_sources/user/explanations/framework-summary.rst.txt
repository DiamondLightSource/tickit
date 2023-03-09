Framework Summary
=================

Tickit is an event-based simulation framework allowing for the simulation of
complex mutli-device systems.

A tickit simulation consists of a scheduler and :doc:`components<components>`, all of which
communicate via a message bus. The scheduler keeps simulation time running and
updates the components in the simulation when required.


.. figure:: ../../images/tickit-overview-full.svg
    :align: center


Components
^^^^^^^^^^
Components in tickit are the fundamental blocks of the simulation.

They are typically comprised of :doc:`devices<devices>` and :doc:`adapters<adapters>`. Devices are created
as required to provide the necessary simulated the behaviour, and adapters are
interfaces between devices and any external input. Adapters allow us to
influence the device from outside the simulation, such as using a TCP client to
alter a parameter on a device.

Using the example Shutter_ to demonstrate. The ``ShutterDevice`` contains the
behaviour, the ``ShutterAdapter`` enables a TCP interface with the shutter, but
the actual ``Shutter`` is the component which encpsulates both.

Scheduler
^^^^^^^^^
The scheduler orchestrates the running of the simulation. It is what is **run** in
a simulation and primarily encapsulates the ticker.

The scheduler is instantiated with :doc:`wiring<wiring>` from the config
file used to start up the simulation. See tutorial :doc:`creating a simulation.<../tutorials/creating-a-simulation>`
With this wiring the scheduler knows which components are connected together and
therfore how to propogate messages and updates through the system.

The **ticker** contains the logic for the propogation of updates through the system.
When a component requests an update, either by a callback or an interupt, the
ticker updates that component then propogates the update to any component
downstream.


Running a tickit simulation
---------------------------

When we *run* a simulation, we first initialise all our components, devices,
adapters and the scheduler. The scheduler runs the system through its inital
**tick**, updating every device in the system. The scheduler will then run
time on, waiting for next time it needs to update system components.

When a device is told to update by the scheduler it takes the current values of
its inputs and runs its update function, returning a device update to the
scheduler. This tells the scheduler it has finished updating, what its outputs
are, and if it wants to be called back for another update (and when). If this
device is wired to another device, the scheduler will then repeat this update
process with all devices downstream of it until they have all updated. The
scheduler will then check if it has been asked by any device to call it back at
a given time. If it has, it will wait until that time then update the device and
again any downstream of it.

Adapters wait to recieve external interaction with the device. When this
interaction causes something to change on the device which is interupting, an
interupt is sent to the scheduler to let it know that the device needs updating
immediately. The scheduler updates that device and then begins the cycle of
updating the rest. When it finishes the tick caused by the interupt, the scheduler
continues to wait until the next update.


.. _Shutter: https://github.com/dls-controls/tickit/blob/master/examples/devices/shutter.py