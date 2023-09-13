tickit
======

|code_ci| |docs_ci| |coverage| |pypi_version| |license|

An event-based multi-device simulation framework providing configuration and
orchestration of complex multi-device simulations.

============== ==============================================================
PyPI           ``pip install tickit``
Source code    https://github.com/dls-controls/tickit
Documentation  https://dls-controls.github.io/tickit
Releases       https://github.com/dls-controls/tickit/releases
============== ==============================================================

An example simulation consists of a simple counter and a sink. The counter
increments up a given value and then passes this value to a sink.

A simulation is defined using a yaml file, in which the graphing of the required
components is denoted. This file defines a **Counter** device named **counter** and
a **Sink** device named **counter_sink**. The output **_value** of **counter** is wired
to the input of **counter_sink**.

.. code-block:: yaml

    - type: examples.devices.counter.Counter
      name: counter
      inputs: {}
    - type: tickit.devices.sink.Sink
      name: counter_sink
      inputs:
        input:
          component: counter
          port: _value


This file is executed to run the simulation.

.. code-block:: bash

    python -m tickit all examples/configs/counter.yaml


The simulation will output logs depicting the incrementing of the counter:

.. code-block:: bash

    DEBUG:examples.devices.counter:Counter initialized with value => 0
    DEBUG:asyncio:Using selector: EpollSelector
    DEBUG:tickit.core.management.ticker:Doing tick @ 0
    DEBUG:tickit.core.components.component:counter got Input(target='counter', time=0, changes=immutables.Map({}))
    DEBUG:examples.devices.counter:Counter incremented to 1
    DEBUG:tickit.core.management.schedulers.base:Scheduler got Output(source='counter', time=0, changes=immutables.Map({'value': 1}), call_at=1000000000)
    DEBUG:tickit.core.management.schedulers.base:Scheduling counter for wakeup at 1000000000
    DEBUG:tickit.core.components.component:counter_sink got Input(target='counter_sink', time=0, changes=immutables.Map({}))
    DEBUG:tickit.devices.sink:Sunk {}
    DEBUG:tickit.core.management.schedulers.base:Scheduler got Output(source='counter_sink', time=0, changes=immutables.Map({}), call_at=None)
    DEBUG:tickit.core.management.ticker:Doing tick @ 1000000000
    DEBUG:tickit.core.components.component:counter got Input(target='counter', time=1000000000, changes=immutables.Map({}))
    DEBUG:examples.devices.counter:Counter incremented to 2
    DEBUG:tickit.core.management.schedulers.base:Scheduler got Output(source='counter', time=1000000000, changes=immutables.Map({'value': 2}), call_at=2000000000)


The counting device is defined as below. It increments a given value and logs as
it increments.

.. code-block:: python

    @dataclass
    class Counter(ComponentConfig):
        """Simple counting device."""

        def __call__(self) -> Component:  # noqa: D102
            return DeviceComponent(
                name=self.name,
                device=CounterDevice(),
                )

    class CounterDevice(Device):
        """A simple device which increments a value."""

        class Inputs(TypedDict):
            ...

        class Outputs(TypedDict):
            value: int

        def __init__(self, initial_value: int = 0, callback_period: int = int(1e9)) -> None:
            self._value = initial_value
            self.callback_period = SimTime(callback_period)
            LOGGER.debug(f"Counter initialized with value => {self._value}")

        def update(self, time: SimTime, inputs: Inputs) -> DeviceUpdate[Outputs]:
            self._value = self._value + 1
            LOGGER.debug(f"Counter incremented to {self._value}")
            return DeviceUpdate(
                CounterDevice.Outputs(value=self._value),
                SimTime(time + self.callback_period),
            )

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
