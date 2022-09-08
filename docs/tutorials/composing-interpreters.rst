Composing Adapters
==================

This tutorial shows how to make use of Interpreter composition when creating an adapter.
The tutorial will follow on from the `Creating an Adapter` tutorial and show how an 
adapter can be made to handle more complex messages by wrapping its ``Interpreter`` in
other helper interpreters.

.. seealso::
    See the `Creating an Adapter` tutorial for a walk-through of creating a basic
    adapter.

In `Creating and Adapter` we saw how to construct an adapter for a ``Shutter`` device
that could receive commands of the form ``P?``, ``T?``, and ``T=1``. To function correctly,
these commands had to be sent exactly as specified, one at a time - when talking to a
simulated device this may not be the case. Rather than worry about more general regex
patterns, interpreter composition can provide a simpler way of dealing with more
complex or messy messages.

Suppose, first of all, that, when communicating with a 'real' shutter device, all
messages are prepended with a fixed-length header that can be ignored. For example,
suppose each message is prepended with a header of 2 bytes like ``/x00/x02P?``,
``\x00\x04T=1.0`` etc. To match the shutter's commands against such messages is
possible with a small modificatiojn of the regex patterns, however, it would be much
neater to cutoff the first two characters of each message before passing it on to the
``CommandInterpreter``. This can be achieved by wrapping the ``CommandInterpreter``
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
    0.2

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

Above, by wrapping the ``ShutterAdapter``'s``CommandInterpreter`` with a
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
