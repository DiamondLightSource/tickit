Adapters
========

Adpaters are user implemented classes associated with a device which facilitate
interactions between that device and components external to the simulation.
Adapters allow us to influence the device from outside the simulation, such as
using a TCP client to alter a parameter on a device. A device may have multiple
adapters simultaneously.

There are four adapters included in the framework:

#. `Composed adapter`_
#. `ZMQ adapter`_
#. `HTTP adapter`_
#. `EPICS adapter`_

Composed adapter
----------------
The composed adapter acts to implement a server and an interpreter. It delegates
the hosting of an external messaging protocol to a server and message handling
to an interpreter.

Tickit currently includes one server implementation, a TCP server, and one
interpreter, the command interpreter. The command interpreter is a generic
interpreter which uses regex to identify commands from incoming messages.

Users may implement their own servers and interpreters and then use the composed
adapter to utilise them for the device.


ZMQ adapter
-----------
An adapter for use on a ZeroMQ data stream.


HTTP adapter
------------
An adapter that hosts an HTTP server, e.g. for devices with REST APIs.


EPICS adapter
-------------
An adapter implementation that acts as an EPICS IOC. It utilises pythonSoftIOC
create an IOC in the process which hosts PV's which can be linked to attributes
on the device.

This is useful for the simulation of devices which use hard IOC's since these
cannot interact with simulated devices.