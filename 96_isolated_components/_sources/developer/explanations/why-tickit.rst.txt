Why was tickit created?
=======================

Tickit is an event-driven multi-device simulation framework. The need for such
a framework came out of the desire to simulate hardware triggered scans. For
such scans, multiple system components are needed to be able to communicate with
one another and have linked behaviour triggered by events.

Tickit allows this by simulating device level logic, and allows the devices to
pass values to each other by the means of device Inputs and Outputs. This flow
of information can be facilitated in memory, or over a message brokering service
for devices distributed across different processes or machines.

The tickit framework was inspired by lewis, a cycle driven simulation framework
by ESS, however differs in key ways to offer different functionality.


multi-device
------------

Lewis only supports running a single device simulation in isolation. Tickit
is designed to allow users to model complex interactions between multiple
devices.

event-based
-----------

Being event based each device in the system only updates when relevent. A
device update can be triggered by interrupts caused by changes from other
linked devices or adapters, or by a devices own scheduled callbacks.

To re-create a cycle driven system a device can be created to request
infinite callbacks at regular intervals which can then go on to update any
downstream device.

Bus based communication
-----------------------

Tickit uses message busses as a basis for the communication between its
devices. This was chosen in an attempt to simplify communication and to try
and produce a less coupled system than is achievable with RPC.

