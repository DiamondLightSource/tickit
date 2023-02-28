Simulate a Single Simple Device
=================================

.. warning::
    There is currently a bug which affects the interaction between isolated
    components and the scheduler. This can be worked around by linking your
    component to a sink. See below for `Bug issue`_ details.


This tutorial shows a user how to create a very simple device and run it in its
own simulation.

In this tutorial we will: 
    
#. `Create a new device`_
#. `Attach an adapter to the device`_
#. `Create the component for the device and adapter`_
#. `Write the config yaml file to run the simulation`_


Following these steps will result in the following simulated system:

.. figure:: ../../images/tickit-simple-simulation.svg
    :align: center


Create a new device
-------------------

Any new device created must: be of type device, have an update method, and must
have **Inputs** and **Outputs** maps as members. In this tutorial we will not
be connecting the device to any other, it will be running in isolation. As a
result the the Inputs and Outputs of this device will be empty, however they
must still be present in the device class.

Initially we set up the boilerplate.

.. code-block:: python

    from tickit.core.device import Device, DeviceUpdate
    from tickit.core.typedefs import SimTime
    from tickit.utils.compat.typing_compat import TypedDict


    class IoCountingDevice(Device):

    #: An empty typed mapping of device inputs
    Inputs: TypedDict = TypedDict("Inputs", {})
    #: A typed mapping containing the current output value
    Outputs: TypedDict = TypedDict("Outputs", {})

    def __init__(self) -> None:

    def update(self, time: SimTime, inputs: Inputs) -> DeviceUpdate[Outputs]:
        return DeviceUpdate(IoBoxDevice.Outputs(), None)


This device we have called IoBoxDevice currently does nothing. It takes no
inputs, provides no outputs and has no attributes that are initialised. Since
we need a device to do something we will make it recieve messages and store it
(until a new one comes along). To do so we can give it an attribute **message**
that is initialised as "Hello".

.. code-block:: python

    from tickit.core.device import Device, DeviceUpdate
    from tickit.core.typedefs import SimTime
    from tickit.utils.compat.typing_compat import TypedDict


    class IoCountingDevice(Device):

    #: An empty typed mapping of device inputs
    Inputs: TypedDict = TypedDict("Inputs", {})
    #: A typed mapping containing the current output value
    Outputs: TypedDict = TypedDict("Outputs", {})

    def __init__(self, inital_value: str = "Hello") -> None:
        self.message = inital_value

    def update(self, time: SimTime, inputs: Inputs) -> DeviceUpdate[Outputs]:
        return DeviceUpdate(IoCountingDevice.Outputs(), None)


Say for some reason we are also interested in how many times the device has
been updated overall. We can do this by initalising another class attribute
**update_count** and having it incremented everytime the device is updated.

.. code-block:: python

    from tickit.core.device import Device, DeviceUpdate
    from tickit.core.typedefs import SimTime
    from tickit.utils.compat.typing_compat import TypedDict


    class IoCountingDevice(Device):

    #: An empty typed mapping of device inputs
    Inputs: TypedDict = TypedDict("Inputs", {})
    #: A typed mapping containing the current output value
    Outputs: TypedDict = TypedDict("Outputs", {})

    def __init__(self, inital_value: str = "Hello") -> None:
        self.message = inital_value
        self.update_count = 0

    def update(self, time: SimTime, inputs: Inputs) -> DeviceUpdate[Outputs]:
        self.update_count = self.update_count + 1
        return DeviceUpdate(IoCountingDevice.Outputs(), None)


For more complicated behaviour you can put logic in the update method and even
call other class functions to manipulate the attributes of the device however
is needed. See the included example devices as a guide.

Now we need a way to give our device a message, we can do so with an adapter.



Attach an adapter to the device
-------------------------------

An adapter facilitaties interactions between a device and components external
to the simulation. In this tutorial we will use a `ComposedAdapter`. Being
composable means it will comprise of a pre-made server and interpreter, delegating
the hosting of an external messaging protocol to a server, and message handling
to an interpreter. Here we wish to use a TCP server and a `CommandInterpreter`
so that we may send the device messages via a TCP client.

The required interpreter and server are initialised with the adapter. We can
keep the server generic for now, but provide the `CommandInterpreter`. 

.. code-block:: python

    from tickit.adapters.composed import ComposedAdapter
    from tickit.adapters.interpreters.command import CommandInterpreter
    from tickit.core.adapter import Server


    class IoCountingAdapater(ComposedAdapter):
        device: IoCountingDevice

        def __init__(self, server: Server) -> None:
            super().__init__(
                server,
                CommandInterpreter(),
            )


When using the CommandInterpreter, commands may be registered by decorating an
adapter method with a command register.

The `CommandInterpreter` interprets messages recived by the server using regex
commands to check the message is something the device wants to handle. Should the
command match, the method is called. We will allow ours to recieve very general
messages:


.. code-block:: python

    from tickit.adapters.composed import ComposedAdapter
    from tickit.adapters.interpreters.command import CommandInterpreter
    from tickit.core.adapter import Server


    class IoCountingAdapater(ComposedAdapter):
        device: IoCountingDevice

        def __init__(self, server: Server) -> None:
            super().__init__(
                server,
                CommandInterpreter(),
            )

        @RegexCommand(r"m=([a-zA-Z0-9_!.?-]+)", interrupt=True, format="utf-8")
        async def set_message(self, value: str) -> None:
            self.device.message = value

        @RegexCommand(r"m\?", format="utf-8")
        async def get_message(self) -> bytes:
            return str(self.device.message).encode("utf-8")


Here we have created two commands for our interpreter, one for setting the value
of the message and and one for getting the message. See the following line:

.. code-block:: python

    @RegexCommand(r"m=([a-zA-Z0-9_!.?-]+)", interrupt=True, format="utf-8")

With this line we register this adapter method as a command so that it is called
if ``m=([a-zA-Z0-9_!.?-]+)`` is recieved. Here ``[a-zA-Z0-9_!.?-]+`` denotes alpha
numberic charaters and some punctuation and forms the capture groups ``()`` for
the message. As a result any message recieved which preceedes with **m=** and
containing characters in the above regex capture group will be stored in the
device with ``self.device.message = value``.

To then query the device for the message we use the command **m?** and the
server will return the current value of **message** on the device.



Create the component for the device and adapter
-----------------------------------------------

In order to now run the device in a simulation we must make a component for it
and the adapter.

The basic format of a component is a follows:

.. code-block:: python

    from dataclasses import dataclass
    from tickit.core.components.component import Component, ComponentConfig
    from tickit.core.components.device_simulation import DeviceSimulation


    @dataclass
    class IoCounter(ComponentConfig):

        def __call__(self) -> Component:  # noqa: D102
            return DeviceSimulation(
                name=self.name,
            )


This is an empty component called ``IoCounter`` whos only atribute is it's name.
To add the device and adapter we include those as arguments to the `__call__`.

.. code-block:: python

    from dataclasses import dataclass
    from tickit.core.components.component import Component, ComponentConfig
    from tickit.core.components.device_simulation import DeviceSimulation
    from tickit.adapters.servers.tcp import TcpServer
    from tickit.utils.byte_format import ByteFormat


    @dataclass
    class IoCounter(ComponentConfig):

        host: str = "localhost"
        port: int = 25565
        format: ByteFormat = ByteFormat(b"%b\r\n")

        def __call__(self) -> Component:  # noqa: D102
            return DeviceSimulation(
                name=self.name,
                device=IoCountingDevice(),
                adapters=[IoCountingAdapater(TcpServer(self.host, self.port, self.format))],
            )

In order to initialise the TCP server we need a host, port and message format.
These can be provided as class attributes but are also able to be assigned from
default values provided in the configuration yaml.

(Note: If the device and adapter are not in the same file as the component they
will also need importing.)



Write the config yaml file to run the simulation
------------------------------------------------

Now we want to run our simulation and talk to our device over a TCP connection.

In order to do so we must first write the config file to run the simulation.
This file will look something like below:


.. code-block:: yaml

    - examples.devices.my_new_device.IoCounter:
        name: MrBox
        host: localhost
        port: 25565
        inputs: {}


Here the first line is the component initialisation and requires the traversal
of the module directory to the component. Following that is name of the component
and the list of its inputs, which in this case is blank.

The simulation can now be run with the following command:

.. code-block:: bash
    
    python -m tickit all path/to/IoCounter_config.yaml

Additionally we will need to start up a client to communicate with the TCP server
of the adapter. We will use the telnet client which can be started with:

.. code-block:: bash

    telnet localhost 25565

When we run this command we expect a response akin to:

.. code-block:: bash

    Trying ::1...
    Connected to localhost.
    Escape character is \'^]\'.

From this telnet client we can send messages and recieve responses from our
adapter. To query the message on the device we use the ``m?`` command:

.. code-block:: bash

    m?
    Hello

Which returns the message we initialised our device with. In order to set a new
message we use the ``m=`` sytnax to set:

.. code-block:: bash

    m=LOUDHELLO

And if we now want to check the message again, the device will return its latest
message.

.. code-block:: bash

    m?
    LOUDHELLO




Bug issue
---------

There is currently an issue with the running of isolated components, such as the
one made in this tutorial. The result of this bug being that any component not
wired to another one, ie one with no inputs or outputs, is invisible to the
scheduler. It does not get updated and feels no passage of time (very unhelpful).

The solution to this for now is to make your device produce some kind of output
and have that output piped into a sink. For example:

.. code-block:: python

    class IoCountingDevice(Device):

        #: An empty typed mapping of device inputs
        Inputs: TypedDict = TypedDict("Inputs", {})
        #: A typed mapping containing the current output value
        Outputs: TypedDict = TypedDict("Outputs", {"message": str})

        def __init__(self, inital_value: str = "Hello") -> None:
            self.message = inital_value
            self.update_count = 0

        def update(self, time: SimTime, inputs: Inputs) -> DeviceUpdate[Outputs]:
            self.update_count = self.update_count + 1
            return DeviceUpdate(IoCountingDevice.Outputs(message=self.message), None)

With the config written as such:

.. code-block:: yaml

    - examples.devices.iobox.IoBox:
        name: MrBox
        inputs: {}
    - tickit.devices.sink.Sink:
        name: sink
        inputs:
        flux: MrBox:message

when the simulation is run ``python -m tickit all path/to/IoCounter_config.yaml`` 
you will see the following:

.. code-block:: bash
    
    DEBUG:asyncio:Using selector: EpollSelector
    DEBUG:tickit.core.management.ticker:Doing tick @ 0
    DEBUG:tickit.core.components.component:MrBox got Input(target='MrBox', time=0, changes=immutables.Map({}))
    DEBUG:tickit.core.management.schedulers.base:Scheduler got Output(source='MrBox', time=0, changes=immutables.Map({'message': 'Hello'}), call_at=None)
    DEBUG:tickit.core.components.component:sink got Input(target='sink', time=0, changes=immutables.Map({'flux': 'Hello'}))
    DEBUG:tickit.devices.sink:Sunk {'flux': 'Hello'}
    DEBUG:tickit.core.management.schedulers.base:Scheduler got Output(source='sink', time=0, changes=immutables.Map({}), call_at=None)

Then if you query it with telnet ``m?``:

.. code-block:: bash

    DEBUG:tickit.adapters.servers.tcp:Recieved b'm?\r\n' from ('127.0.0.1', 38986)
    DEBUG:tickit.adapters.servers.tcp:Replying with b'Hello'

Setting the new value ``m=LOUDHELLO``:

.. code-block:: bash

    DEBUG:tickit.adapters.servers.tcp:Recieved b'm=LOUNDHELLO\r\n' from ('127.0.0.1', 38986)
    DEBUG:tickit.core.management.schedulers.base:Scheduler got Interrupt(source='MrBox')
    DEBUG:tickit.core.management.schedulers.base:Scheduling MrBox for wakeup at 88696390177
    DEBUG:tickit.core.management.ticker:Doing tick @ 88696390177
    DEBUG:tickit.core.components.component:MrBox got Input(target='MrBox', time=88696390177, changes=immutables.Map({}))
    DEBUG:tickit.core.management.schedulers.base:Scheduler got Output(source='MrBox', time=88696390177, changes=immutables.Map({'message': 'LOUNDHELLO'}), call_at=None)
    DEBUG:tickit.core.components.component:sink got Input(target='sink', time=88696390177, changes=immutables.Map({'flux': 'LOUNDHELLO'}))
    DEBUG:tickit.devices.sink:Sunk {'flux': 'LOUNDHELLO'}
    DEBUG:tickit.core.management.schedulers.base:Scheduler got Output(source='sink', time=88696390177, changes=immutables.Map({}), call_at=None)

Then querying the new ``m?``:

.. code-block:: bash

    DEBUG:tickit.adapters.servers.tcp:Recieved b'm?\r\n' from ('127.0.0.1', 38986)
    DEBUG:tickit.adapters.servers.tcp:Replying with b'LOUNDHELLO'



.. _ComposedAdapter: <tickit.adapters.composed.ComposedAdapter>
.. _CommandInterpreter: <tickit.adapters.interpreters.command_interpreter.CommandInterpreter>