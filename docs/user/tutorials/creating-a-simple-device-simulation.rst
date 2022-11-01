Making a simple device simulation
=================================

This tutorial shows a user how to create a very simple device and run it within
its own simulation.

Any new device created must be of type device, have an update method, and must
have **Inputs** and **Outputs** maps as members. In this tutorial we will not
be connecting the device to any other, it will be running in isolation. As a
result the the Inputs and Outputs of this device will be empty, however they
must still be present.