Use Command Interpreter Wrappers
================================

In `Using an Adapter` we saw how to use a composed adapter with the amplifier
device so that it could receive commands of the form ``A?`` and ``A=4.4`` to get
and set values to the device. These commands had to be sent exactly as specified
and individually. However, when talking to a simulated device this may not be the
case. Our simulated device may recieve more complex messages and as a result our
command interprerter needs to be able to handle them.

This can be achieved by wrapping the `CommandInterpreter` in other helper interpreters.
This allows us to do some pre/post processing on all commands before/after they
are handled.

There are three such wrappers:

#. `Beheading Interpreter`_
#. `Splitting Interpreter`_
#. `Joining Interpreter`_

The use of such wrappers will be demonstrated with the example Shutter_ device.


Beheading Interpreter
---------------------

Suppose that when communicating with a real shutter device, all messages are
prepended with a fixed-length header that can be ignored. For example each message
being prepended with a header of 2 bytes: ``\x00\x02P?``, ``\x00\x04T=1.0`` etc. 

Our simulated device needs to handle messages of the same form. 

We could use regex pattern matching to avoid this header but in some cases this is
not desirable. In such cases we can cutoff the first two characters of each message
before passing it on to the ``CommandInterpreter`` by wrapping the ``CommandInterpreter``
with a ``BeheadingInterpreter`` in the adapter's ``__init__`` as follows:

.. code-block:: python

    from typing import Awaitable, Callable
    from tickit.adapters.interpreters.command import CommandInterpreter
    from tickit.adapters.interpreters.wrappers import BeheadingInterpreter
    from tickit.adapters.servers.tcp import TcpServer
    from tickit.core.adapter import Adapter
    class ShutterAdapter(Adapter):
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
                BeheadingInterpreter(CommandInterpreter(), header_size=2),
            )


With the rest of the adapter unchanged. The adapter will then correctly interpret
commands in messages with the header attached:

.. code-block:: bash

    \x00\x02P?
    2.0


Splitting Interpreter
---------------------

Now suppose that we would like to be able to send multiple commands in a single
message, separated by some delimiter. For example, though ``P?`` and ``T?`` are
interpreted as commands by the ``ShutterAdapter``, ``P? T?`` is not:

.. code-block:: bash

    P?
    0.2
    T?
    0.2
    P? T?
    Request does not match any known command

This is the usecase of ``SplittingInterpreter``. This splits a message into multiple
sub-messages and then passes them on to another interprerter that it wraps. Wrapping
the adapter's ``CommandInterprerter`` as

.. code-block:: python

    SplittingInterpreter(CommandInterpreter(), delimiter=b" ") 
    
with the rest of the adapter unchanged, allows for interpreting commands separated by
a space:

.. code-block:: bash

    P?
    0.2
    T?
    0.2
    P? T?
    0.2
    0.2

A wrapped adapter can be wrapped by another adapter wrapper. Combining the two above
examples as

.. code-block:: python
    
    BeheadingInterpreter(
        SplittingInterpreter(
            CommandInterpreter(), delimiter=b" "
        ),
        header_size=2
    )

allows for the adapter to deal with messages with a fixed-length header containing
multiple commands separated by a space:

.. code-block:: bash

    \x00\x02P?
    0.2
    \x00\x05P? T?
    0.2
    0.2

So far we have only seen interpreter wrappers altering the recieved message before
passing it on to another interpreter. There are also wrappers that alter the response
received from the wrapped interpreter before it is sent back.


Joining Interpreter
-------------------

Above, by wrapping the ``ShutterAdapter``'s ``CommandInterpreter`` with a
``SplittingInterpreter`` we were able to execute multiple commands from a single
message. Each executed command sent its own response, i.e. one message resulted in
multiple responses. We may instead want each message to have its own response
containing multiple command responses. This is the usecase for ``JoiningInterpreter``.
Wrapping the ``SplittingInterpreter`` with this will join each of the responses into a
single message.

.. code-block:: python

    JoiningInterpreter(
        BeheadingInterpreter(
            SplittingInterpreter(
                CommandInterpreter(), delimiter=b" "
            ),
            header_size=2
        ),
        response_delimiter=b" "
    )

Results in

.. code-block:: bash

    P?
    0.2
    T?
    0.2
    P? T?
    0.2 0.2


.. _Shutter: https://github.com/dls-controls/tickit/blob/master/examples/devices/shutter.py