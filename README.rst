tickit
======

|code_ci| |docs_ci| |coverage| |pypi_version| |license|

An event-based multi-device simulation framework providing configuration and
orchestration of complex multi-device simulations.

============== ==============================================================
PyPI           ``pip install tickit``
Source code    https://github.com/dls-controls/tickit
Documentation  https://dls-controls.github.io/tickit
Changelog      https://github.com/dls-controls/tickit/blob/master/CHANGELOG.rst
============== ==============================================================

An example device which emits a random value between *0* and *255* whenever
called and asks to be called again once the simulation has progressed by the
``callback_period``:

.. code-block:: python

    class RandomTrampoline(ConfigurableDevice):

    Inputs: TypedDict = TypedDict("Inputs", {})
    Outputs: TypedDict = TypedDict("Outputs", {"output": int})

    def __init__(self, callback_period: int = int(1e9)) -> None:
        self.callback_period = SimTime(callback_period)

    def update(self, time: SimTime, inputs: Inputs) -> DeviceUpdate[Outputs]:
        output = randint(0, 255)
        LOGGER.debug(
            "Boing! (delta: {}, inputs: {}, output: {})".format(time, inputs, output)
        )
        return DeviceUpdate(
            RandomTrampoline.Outputs(output=output),
            SimTime(time + self.callback_period),
        )


An example simulation defines a **RemoteControlled** device named **tcp_contr**
and a **Sink** device named **contr_sink**. The **observed** output of
**tcp_contr** is wired to the **input** input of **contr_sink**. Additionally,
extenal control of **tcp_contr** is afforded by a **RemoteControlledAdapter**
which is exposed extenally through a **TCPServer**:

.. code-block:: yaml

    - tickit.core.components.device_simulation.DeviceSimulation:
        adapters:
        - examples.devices.remote_controlled.RemoteControlledAdapter:
            server:
            tickit.adapters.servers.tcp.TcpServer:
                format: "%b\r\n"
        device:
          examples.devices.remote_controlled.RemoteControlled: {}
        inputs: {}
        name: tcp_contr
    - tickit.core.components.device_simulation.DeviceSimulation:
        adapters: []
        device:
          tickit.devices.sink.Sink: {}
        inputs:
          input: tcp_contr:observed
        name: contr_sink


.. |code_ci| image:: https://github.com/dls-controls/tickit/workflows/Code%20CI/badge.svg?branch=master
    :target: https://github.com/dls-controls/tickit/actions?query=workflow%3A%22Code+CI%22
    :alt: Code CI

.. |docs_ci| image:: https://github.com/dls-controls/tickit/workflows/Docs%20CI/badge.svg?branch=master
    :target: https://github.com/dls-controls/tickit/actions?query=workflow%3A%22Docs+CI%22
    :alt: Docs CI

.. |coverage| image:: https://codecov.io/gh/dls-controls/tickit/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/dls-controls/tickit
    :alt: Test Coverage

.. |pypi_version| image:: https://img.shields.io/pypi/v/tickit.svg
    :target: https://pypi.org/project/tickit
    :alt: Latest PyPI version

.. |license| image:: https://img.shields.io/badge/License-Apache%202.0-blue.svg
    :target: https://opensource.org/licenses/Apache-2.0
    :alt: Apache License

..
    Anything below this line is used when viewing README.rst and will be replaced
    when included in index.rst

See https://dls-controls.github.io/tickit for more detailed documentation.
