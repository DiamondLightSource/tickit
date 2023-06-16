Using an Adapter
================

This tutorial shows how to use a simple adapter to externally interact with a
device in the tickit framework.

We will use a `ComposedAdapter` which will act as a simple TCP interface to the
``Amplifier`` device we created in the previous how-to.

.. seealso::
    See the `Creating a Device` how-to for a walk-through of creating the Amplifier
    device.

We will be using a composed adapter with a TCP server and the command interprerter.
For more information on adapters see :doc:`here<../explanations/adapters>`.

Initialise Adapter
------------------

We shall begin using the same ``amp.py`` file from the ``Amplifier`` device. In 
that file add a new ``AmplifierAdapter`` class which inherets `ComposedAdapter`.
Within ``AmplifierAdapter`` we need to assign the ``AmplifierDevice`` as a class
member, and initialise the the server and interprerter like so:

.. code-block:: python

    from tickit.adapters.composed import ComposedAdapter
    from tickit.adapters.interpreters.command.command_interpreter import CommandInterpreter
    from tickit.adapters.servers.tcp import TcpServer
    from tickit.utils.byte_format import ByteFormat


    class AmplifierAdapter(ComposedAdapter):
        device: AmplifierDevice

        def __init__(
            self,
            host: str = "localhost",
            port: int = 25565,
        ) -> None:
            super().__init__(
                TcpServer(host, port, ByteFormat(b"%b\r\n")),
                CommandInterpreter(),
            )


Adapter Commands
----------------

Now we have an adapter for our device, we need to tell it how to identify commands.
When using the `CommandInterpreter`, commands may be registered by decorating an
adapter method with a command register.

We shall create two methods, one which returns the current amplification of the
device, and another which sets a new value for the amplification.

We shall begin by creating a method which returns the current value of the
amplification. To do this we register it as a `RegexCommand` which is called by
sending ``A?``. Since reading a device value will not alter the device state we
shall set ``interrupt`` to ``False``. We shall also specify that the byte encoded
message should be decoded to a string prior to matching using the ``utf-8`` standard.

.. code-block:: python

    class AmplifierAdapter(ComposedAdapter):

         ...

        @RegexCommand(r"A\?", False, "utf-8")
        async def get_amplification(self) -> bytes:
            return str(self.device.amplification).encode("utf-8")


We shall now add a method which sets a new value for the amplification when
``A=(\d+\.?\d*)`` is recieved, where ``\d+\.?\d*`` denotes a decimal number and the
parentheses form the capture group from which the argument is extracted.

.. code-block:: python

    class AmplifierAdapter(ComposedAdapter):

        ...

        @RegexCommand(r"A=(\d+\.?\d*)", True, "utf-8")
        async def set_amplification(self, amplification: float) -> None:
            self.device.amplification = amplification


In its entirety your addapter should look as below.

.. code-block:: python

    from tickit.adapters.composed import ComposedAdapter
    from tickit.adapters.interpreters.command.command_interpreter import CommandInterpreter
    from tickit.adapters.interpreters.command.regex_command import RegexCommand
    from tickit.adapters.servers.tcp import TcpServer
    from tickit.utils.byte_format import ByteFormat


    class AmplifierAdapter(ComposedAdapter):
    device: AmplifierDevice

        def __init__(
            self,
            host: str = "localhost",
            port: int = 25565,
        ) -> None:
            super().__init__(
                TcpServer(host, port, ByteFormat(b"%b\r\n")),
                CommandInterpreter(),
            )

        @RegexCommand(r"A\?", False, "utf-8")
        async def get_amplification(self) -> bytes:
            return str(self.device.amplification).encode("utf-8")

        @RegexCommand(r"A=(\d+\.?\d*)", True, "utf-8")
        async def set_amplification(self, amplification: float) -> None:
            self.device.amplification = amplification


include the Adapter
-------------------

In order to now use this adapter to control our device we need to include it in
our amplifier `ComponentConfig`. To do this we simply add it to the arguments of
`DeviceSimulation`.

.. code-block:: python

    @dataclass
    class Amplifier(ComponentConfig):
        initial_amplification: int

        def __call__(self) -> Component:
            return DeviceSimulation(
                name=self.name,
                device=AmplifierDevice(
                    initial_amplification=self.initial_amplification,
                ),
                adapters=[AmplifierAdapter()],
            )

It is possible to add many adapters to a device, for example a composed and an epics
adapter. To do this simply list them.


Using the Adapter
-----------------

The simulation can be run the same as before using the yaml.

.. code-block:: bash

    python -m tickit all amp_conf.yaml

Additionally, we will start a telnet client which communicates with the TcpServer of
the adapter, this may be performed by running the following command:

.. code-block:: bash

    telnet localhost 25565

When run we expect a response akin to:

.. code-block:: bash

    Trying ::1...
    Connected to localhost.
    Escape character is \'^]\'.

From this telnet client we can send various messages and recieve responses from our
adapter. The only messages our adapter will recognise are ``A?`` and ``A=``, so we
enquire for the current amplification.

.. code-block:: bash

    A?
    2.0

It tells us 2.

Finally, we may wish to set a new amplification with ``A=``. Here is an example of
setting a new amplification of 4.4 with accompanying tickit debug output:

.. code-block:: bash

    A=4.4

.. code-block:: bash

    DEBUG:asyncio:Using selector: EpollSelector
    DEBUG:tickit.core.management.ticker:Doing tick @ 0
    DEBUG:tickit.core.components.component:source got Input(target='source', time=0, changes=immutables.Map({}))
    DEBUG:tickit.devices.source:Sourced 10.0
    DEBUG:tickit.core.management.schedulers.base:Scheduler got Output(source='source', time=0, changes=immutables.Map({'value': 10.0}), call_at=None)
    DEBUG:tickit.core.components.component:amp got Input(target='amp', time=0, changes=immutables.Map({'initial_signal': 10.0}))
    DEBUG:tickit.core.management.schedulers.base:Scheduler got Output(source='amp', time=0, changes=immutables.Map({'amplified_signal': 20.0}), call_at=None)
    DEBUG:tickit.core.components.component:sink got Input(target='sink', time=0, changes=immutables.Map({'input': 20.0}))
    DEBUG:tickit.devices.sink:Sunk {'input': 20.0}
    DEBUG:tickit.core.management.schedulers.base:Scheduler got Output(source='sink', time=0, changes=immutables.Map({}), call_at=None)
    DEBUG:tickit.adapters.servers.tcp:Recieved b'A=4.4\r\n' from ('127.0.0.1', 56930)
    DEBUG:tickit.core.management.schedulers.base:Scheduler got Interrupt(source='amp')
    DEBUG:tickit.core.management.schedulers.base:Scheduling amp for wakeup at 17846862439
    DEBUG:tickit.core.management.ticker:Doing tick @ 17846862439
    DEBUG:tickit.core.components.component:amp got Input(target='amp', time=17846862439, changes=immutables.Map({}))
    DEBUG:tickit.core.management.schedulers.base:Scheduler got Output(source='amp', time=17846862439, changes=immutables.Map({'amplified_signal': 44.0}), call_at=None)
    DEBUG:tickit.core.components.component:sink got Input(target='sink', time=17846862439, changes=immutables.Map({'input': 44.0}))
    DEBUG:tickit.devices.sink:Sunk {'input': 44.0}
    DEBUG:tickit.core.management.schedulers.base:Scheduler got Output(source='sink', time=17846862439, changes=immutables.Map({}), call_at=None)


Here we see the inital tick at time=0 which initalises the system. We see the
source providing a signal of 10, the amplifier getting the value of 10,
amplifiying it to 20 and outputing it to the sink, which takes it. You then see
the adapter interupting and changing the amplification to 4.4, continuting the
same pattern but with the sink finally recieving a input signal of 44.