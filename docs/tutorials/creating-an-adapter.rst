Creating an Adapter
===================

This tutorial shows how to create a simple `Adapter` for use in the ticket framework.
This adapter will act as a simple TCP interface to the `Shutter` device which can vary
the transmission of ``flux`` by changing ``position``. The `Adapter` we create will be
composable, meaning it will comprise of a pre-made `Server` and `Interpreter`.

.. seealso::
    See the `Creating a Device` tutorial for a walk-through of creating the `Shutter`
    device.

Adapter Module File
-------------------

We shall begin by creating a new python module named ``my_shutter_adapter.py``, and
open it with our preferred editor. This file will be used to store the our
ShutterAdapter class which will determine the operation of our adapter.

Adapter Class
-------------

We shall begin by defining the ShutterAdapter class which inherits
`ConfigurableAdapter` - by doing so a configuration dataclass will automatically be
created for the adapter, allowing easy YAML configuration.

.. code-block:: python

    from tickit.adapters.composed import ComposedAdapter
    from tickit.core.adapter import ConfigurableAdapter

    class ShutterAdapter(ComposedAdapter, ConfigurableAdapter):

Adapter Constructor and Configuration
-------------------------------------

Next, we shall create the ``__init__`` method, allowing for the adapter to be
instantiated. The first two arguments of an adapter ``__init__`` must be ``device`` of
type ``Device`` and ``raise_interrupt`` of type ``Callable[[], Awaitable[None]]``, to
which the device the adapter acts upon and a method used to request an immediate update
of the device are passed respectively. Additionally, we will include the arguments
``host`` and ``port`` which will be used to configure our ``TcpServer``. With these we
will instantiate a composed adapter with a ``TcpServer`` which formats sent messages by
appending a line break and a ``CommandInterpreter``.

.. code-block:: python

    from typing import Awaitable, Callable

    from tickit.adapters.composed import ComposedAdapter
    from tickit.adapters.interpreters.command.command_interpreter import CommandInterpreter
    from tickit.adapters.servers.tcp import TcpServer
    from tickit.core.adapter import ConfigurableAdapter

    class ShutterAdapter(ComposedAdapter, ConfigurableAdapter):
        def __init__(
            self,
            device: Shutter,
            raise_interrupt: Callable[[], Awaitable[None]],
            host: str = "localhost",
            port: int = 25565,
        ) -> None:
            super().__init__(
                device,
                raise_interrupt,
                TcpServer(host, port, ByteFormat(b"%b\r\n")),
                CommandInterpreter(),
            )

.. note::
    Arguments to the ``__init__`` method may be specified in the simulation config file
    if the device inherits `ConfigurableAdapter` (excluding ``device`` and
    ``raise_interrupt`` which are injected at run-time).

Adapter Commands
----------------

When using the `CommandInterpreter`, commands may be registered by decorating an
adapter method with a command register. We shall begin by creating a method which
returns the current position of the `Shutter` and register it as a `RegexCommand` which
is called by sending ``P?``. Since reading will not alter the device state we shall set
``interrupt`` to ``False``. We shall also specify that the byte encoded message should
be decoded to a string prior to matching using the ``utf-8`` standard.

.. code-block:: python

    from tickit.adapters.composed import ComposedAdapter
    from tickit.adapters.interpreters.command.regex_command import RegexCommand
    from tickit.core.adapter import ConfigurableAdapter

    class ShutterAdapter(ComposedAdapter, ConfigurableAdapter):
        
        ...

        @RegexCommand(r"P\?", False, "utf-8")
        async def get_position(self) -> bytes:
            return str(self._device.position).encode("utf-8")

We shall add a similar command to read back the current target position of the
`Shutter` when ``T?`` is recieved.

.. code-block:: python

    from tickit.adapters.composed import ComposedAdapter
    from tickit.adapters.interpreters.command.regex_command import RegexCommand
    from tickit.core.adapter import ConfigurableAdapter

    class ShutterAdapter(ComposedAdapter, ConfigurableAdapter):
        
        ...

        @RegexCommand(r"T\?", False, "utf-8")
        async def get_target(self) -> bytes:
            return str(self._device.target_position).encode("utf-8")

Next, we shall add a method which sets a new target position for the `Shutter` when
``T=(\d+\.?\d*)`` is recieved, where ``\d+\.?\d*`` denotes a decimal number and the
parentheses form the capture group from which the argument is extracted.

.. code-block:: python

    from tickit.adapters.composed import ComposedAdapter
    from tickit.adapters.interpreters.command.regex_command import RegexCommand
    from tickit.core.adapter import ConfigurableAdapter

    class ShutterAdapter(ComposedAdapter, ConfigurableAdapter):
        
        ...

        @RegexCommand(r"T=(\d+\.?\d*)", True, "utf-8")
        async def set_target(self, target: str) -> None:
            self._device.target_position = float(target)
            self._device.last_time = None

Using the Adapter
-----------------

In order to use the device we must first create a simulation configuration file, we
shall create one named ``my_shutter_simulation.yaml``, and open it with our preferred
editor. This file will be used to set up a simulation consisting of a `Source` named
source which will produce a constant flux, the shutter which will act on the flux as
per our implementation, and a `Sink` named sink which will recieve the resulting flux.
The shutter will be given a ShutterAdapter which uses the default configuration for
``host`` and ``port``. 

.. code-block:: yaml

    - tickit.core.components.device_simulation.DeviceSimulation:
        adapters: []
        device:
            tickit.devices.source.Source:
                value: 42.0
        inputs: {}
        name: source
    - tickit.core.components.device_simulation.DeviceSimulation:
        adapters:
        - examples.devices.shutter.ShutterAdapter: {}
        device:
            examples.devices.shutter.Shutter:
                default_position: 0.2
                initial_position: 0.24
        inputs:
            flux: source:value
        name: shutter
    - tickit.core.components.device_simulation.DeviceSimulation:
        adapters: []
        device:
            tickit.devices.sink.Sink: {}
        inputs:
            flux: shutter:flux
        name: sink

.. seealso::
    See the `Creating a Simulation` tutorial for a walk-through of creating simulation
    configurations.

We may then run the simulation, this may be performed by running the following command:

.. code-block:: bash

    python -m tickit all my_shutter_simulation.yaml

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
adapter. Examples of getting the position and target with ``P?`` and ``T?`` are shown
below:

.. code-block:: bash

    P?
    0.2

.. code-block:: bash

    T?
    0.2

Finally, we may wish to set a new target with ``T=``, an example of this with the value
0.16 is shown below, with accompanying tickit debug output:

.. code-block:: bash

    T=0.16

.. code-block:: bash

    DEBUG:tickit.adapters.servers.tcp:Recieved b'T=0.16\r\n' from ('::1', 33096, 0, 0)
    DEBUG:tickit.core.management.schedulers.base:Scheduler got Interrupt(source='shutter')
    DEBUG:tickit.core.management.schedulers.base:Scheduling Wakeup(component='shutter', when=209786950024)
    DEBUG:tickit.core.management.ticker:Doing tick @ 209786950024
    DEBUG:tickit.core.components.component:shutter got Input(target='shutter', time=209786950024, changes=immutables.Map({}))
    DEBUG:tickit.core.management.schedulers.base:Scheduler got Output(source='shutter', time=209786950024, changes=immutables.Map({}), call_in=100000000)
    DEBUG:tickit.core.management.schedulers.base:Scheduling Wakeup(component='shutter', when=209886950024)
    DEBUG:tickit.core.components.component:sink got Input(target='sink', time=209786950024, changes=immutables.Map({}))
    DEBUG:tickit.devices.sink:Sunk {'flux': 8.4}
    DEBUG:tickit.core.management.schedulers.base:Scheduler got Output(source='sink', time=209786950024, changes=immutables.Map({}), call_in=None)
    DEBUG:tickit.core.management.ticker:Doing tick @ 209886950024
    DEBUG:tickit.core.components.component:shutter got Input(target='shutter', time=209886950024, changes=immutables.Map({}))
    DEBUG:tickit.core.management.schedulers.base:Scheduler got Output(source='shutter', time=209886950024, changes=immutables.Map({'flux': 7.5600000000000005}), call_in=100000000)
    DEBUG:tickit.core.management.schedulers.base:Scheduling Wakeup(component='shutter', when=209986950024)
    DEBUG:tickit.core.components.component:sink got Input(target='sink', time=209886950024, changes=immutables.Map({'flux': 7.5600000000000005}))
    DEBUG:tickit.devices.sink:Sunk {'flux': 7.5600000000000005}
    DEBUG:tickit.core.management.schedulers.base:Scheduler got Output(source='sink', time=209886950024, changes=immutables.Map({}), call_in=None)
    DEBUG:tickit.core.management.ticker:Doing tick @ 209986950024
    DEBUG:tickit.core.components.component:shutter got Input(target='shutter', time=209986950024, changes=immutables.Map({}))
    DEBUG:tickit.core.management.schedulers.base:Scheduler got Output(source='shutter', time=209986950024, changes=immutables.Map({'flux': 6.7200000000000015}), call_in=100000000)
    DEBUG:tickit.core.management.schedulers.base:Scheduling Wakeup(component='shutter', when=210086950024)
    DEBUG:tickit.core.components.component:sink got Input(target='sink', time=209986950024, changes=immutables.Map({'flux': 6.7200000000000015}))
    DEBUG:tickit.devices.sink:Sunk {'flux': 6.7200000000000015}
    DEBUG:tickit.core.management.schedulers.base:Scheduler got Output(source='sink', time=209986950024, changes=immutables.Map({}), call_in=None)
    DEBUG:tickit.core.management.ticker:Doing tick @ 210086950024
    DEBUG:tickit.core.components.component:shutter got Input(target='shutter', time=210086950024, changes=immutables.Map({}))
    DEBUG:tickit.core.management.schedulers.base:Scheduler got Output(source='shutter', time=210086950024, changes=immutables.Map({'flux': 6.72}), call_in=None)
    DEBUG:tickit.core.components.component:sink got Input(target='sink', time=210086950024, changes=immutables.Map({'flux': 6.72}))
    DEBUG:tickit.devices.sink:Sunk {'flux': 6.72}
    DEBUG:tickit.core.management.schedulers.base:Scheduler got Output(source='sink', time=210086950024, changes=immutables.Map({}), call_in=None)

.. seealso::
    See the `Running a Simulation` tutorial for a walk-through of running a simulation
    in a single or across multiple processes.