Why was tickit created?
=======================

Tickit is an event-driven multi-device simulation framework. The need for such
a framework came out of the desire to simulate hardware triggered scans. For
such scans, multiple system components are needed to be able to communicate with
one another and have linked behaviour triggered by events.

Tickit allows this by simulating device level logic, and allows the devices to
pass values to each other by the means of device Inputs and Outputs. Each device
takes its inputs off of and puts its outputs on to a message bus. This can be
done in memory, or over a message brokering service.

The tickit framework was inspired by lewis, a cycle drive simulation framework
by ESS, however differs in key ways to offer different functionality.

event-based:
    Being event based each device in the system only updates when relevent. A
    device update can be triggered by interrupts caused by changes from other
    linked devices or adapters, or by a devices own scheduled callbacks.

    To re-create a cycle driven system a device can be created to request
    infinite callbacks at regular intervals which can then go on to update any
    downstream device.

