Using an Adapter
================

This tutorial shows how to use a simple adapter to externally interact with a
device in the tickit framework.

We will use a ``CommandAdapter`` which will act as a simple TCP interface to the
``Amplifier`` device we created in the previous how-to.

.. seealso::
    See the `Creating a Device` how-to for a walk-through of creating the Amplifier
    device.

For more information on adapters see :doc:`here<../explanations/adapters>`.

Initialise Adapter
------------------

We shall begin using the same ``amplifier.py`` file from the ``Amplifier`` device. In
that file add a new ``AmplifierAdapter`` class which inherits ``CommandAdapter``.


.. code-block:: python

    from tickit.adapters.tcp import CommandAdapter
    from tickit.utils.byte_format import ByteFormat


    class AmplifierAdapter(CommandAdapter):
        device: AmplifierDevice

        def __init__(self, device: AmplifierDevice) -> None:
            super().__init__()
            self.device = device


Adapter Commands
----------------

Now we have an adapter for our device, we need to tell it how to identify commands.
Commands are registered by decorating an adapter method with a command register.

We shall create two methods, one which returns the current amplification of the
device, and another which sets a new value for the amplification.

We shall begin by creating a method which returns the current value of the
amplification. To do this we register it as a ``RegexCommand`` which is called by
sending ``A?``. Since reading a device value will not alter the device state we
shall set ``interrupt`` to ``False``. We shall also specify that the byte encoded
message should be decoded to a string prior to matching using the ``utf-8`` standard.

.. code-block:: python

    from tickit.adapters.specifications import RegexCommand

    class AmplifierAdapter(CommandAdapter):

         ...

        @RegexCommand(r"A\?", False, "utf-8")
        async def get_amplification(self) -> bytes:
            return str(self.device.amplification).encode("utf-8")


We shall now add a method which sets a new value for the amplification when
``A=(\d+\.?\d*)`` is received, where ``\d+\.?\d*`` denotes a decimal number and the
parentheses form the capture group from which the argument is extracted.

.. code-block:: python

    class AmplifierAdapter(CommandAdapter):

        ...

        @RegexCommand(r"A=(\d+\.?\d*)", True, "utf-8")
        async def set_amplification(self, amplification: float) -> None:
            self.device.amplification = amplification


We also optionally want to have messages formatted more nicely so can set the
``_byte_format`` to something slightly more readable. In its entirety your
adapter should look as below.

.. code-block:: python

    from tickit.adapters.tcp import CommandAdapter
    from tickit.utils.byte_format import ByteFormat
    from tickit.adapters.specifications import RegexCommand

    class AmplifierAdapter(CommandAdapter):
        device: AmplifierDevice
        _byte_format: ByteFormat = ByteFormat(b"%b\r\n")

        def __init__(self, device: AmplifierDevice) -> None:
            super().__init__()
            self.device = device

        @RegexCommand(r"A\?", False, "utf-8")
        async def get_amplification(self) -> bytes:
            return str(self.device.amplification).encode("utf-8")

        @RegexCommand(r"A=(\d+\.?\d*)", True, "utf-8")
        async def set_amplification(self, amplification: float) -> None:
            self.device.amplification = amplification


Include the Adapter
-------------------

In order to now use this adapter to control our device we need to include it in
our amplifier `ComponentConfig`. To do this we first construct an `AdapterContainer`
with our ``AmplifierAdapter`` and the appropriate `AdapterIo`. In this case ``TcpIo``.
Once this is done we simply add it to the arguments of `DeviceComponent`. 

.. code-block:: python

    @pydantic.v1.dataclasses.dataclass
    class Amplifier(ComponentConfig):
        """Amplifier you can set the amplification value of over TCP."""

        initial_amplification: int
        host: str = "localhost"
        port: int = 25565

        def __call__(self) -> Component:  # noqa: D102
            device = AmplifierDevice(
                initial_amplification=self.initial_amplification,
            )
            adapters = [
                AdapterContainer(
                    AmplifierAdapter(device),
                    TcpIo(
                        self.host,
                        self.port,
                    )
            ]
            return DeviceComponent(
                name=self.name,
                device=device,
                adapters=adapters,
            )

It is possible to add many adapters to a device, for example a composed and an epics
adapter. To do this simply list them.


Using the Adapter
-----------------

The simulation can be run the same as before using the yaml.

.. code-block:: bash

    python -m tickit all amplifier.yaml

Additionally, we will start a telnet client which communicates with the TcpServer of
the adapter, this may be performed by running the following command:

.. code-block:: bash

    telnet localhost 25565

When run we expect a response akin to:

.. code-block:: bash

    Trying ::1...
    Connected to localhost.
    Escape character is \'^]\'.

From this telnet client we can send various messages and receive responses from our
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
    DEBUG:tickit.adapters.servers.tcp:Received b'A=4.4\r\n' from ('127.0.0.1', 56930)
    DEBUG:tickit.core.management.schedulers.base:Scheduler got Interrupt(source='amp')
    DEBUG:tickit.core.management.schedulers.base:Scheduling amp for wakeup at 17846862439
    DEBUG:tickit.core.management.ticker:Doing tick @ 17846862439
    DEBUG:tickit.core.components.component:amp got Input(target='amp', time=17846862439, changes=immutables.Map({}))
    DEBUG:tickit.core.management.schedulers.base:Scheduler got Output(source='amp', time=17846862439, changes=immutables.Map({'amplified_signal': 44.0}), call_at=None)
    DEBUG:tickit.core.components.component:sink got Input(target='sink', time=17846862439, changes=immutables.Map({'input': 44.0}))
    DEBUG:tickit.devices.sink:Sunk {'input': 44.0}
    DEBUG:tickit.core.management.schedulers.base:Scheduler got Output(source='sink', time=17846862439, changes=immutables.Map({}), call_at=None)


Here we see the initial tick at time=0 which initialises the system. We see the
source providing a signal of 10, the amplifier getting the value of 10,
amplifying it to 20 and outputting it to the sink, which takes it. You then see
the adapter interrupting and changing the amplification to 4.4, continuing the
same pattern but with the sink finally receiving a input signal of 44.
