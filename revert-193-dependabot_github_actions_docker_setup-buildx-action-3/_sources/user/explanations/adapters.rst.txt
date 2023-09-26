Adapters
========

Adapters are user implemented classes associated with a device which facilitate
interactions between that device and components external to the simulation.
Adapters allow us to influence the device from outside the simulation, such as
using a TCP client to alter a parameter on a device. A device may have multiple
adapters simultaneously.

Adapters are implemented within `AdapterContainer` and these containers are added
to the device or system simulations. An AdapterContainer simply takes an adapter and
an appropriate `AdapterIo`. When the container is run, it sets up the io with the 
specific adapter.

- The Adapter contains the device specific interface for a given io type.
- The `AdapterIo` contains IO logic which is agnositc to the details of the device.

There are four adapter types included in the framework:

#. `Command adapter`_
#. `ZMQ adapter`_
#. `HTTP adapter`_
#. `EPICS adapter`_


Command adapter
----------------
The command adapter identifies and handles commands from incoming messages and is 
utilised with ``TcpIo``. Commands are defined via decoration of adapter methods and the
only such command type currently is a ``RegexCommand``. This matches incoming messages to
regex patterns and processes the command appropriately.


ZMQ adapter
-----------
An adapter for use on a ZeroMQ data stream.


HTTP adapter
------------
An adapter that utilises HTTP endpoints for the ``HttpIo``.


EPICS adapter
-------------
An adapter implementation that acts as an EPICS IOC. It utilises pythonSoftIOC
create an IOC in the process which hosts PVs which can be linked to attributes
on the device.

This is useful for the simulation of devices which use hard IOCs since these
cannot interact with simulated devices.
