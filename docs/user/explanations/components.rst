Simulation Components
=====================

There are two types of components that can be used in a tickit simulation,
device components and system components.

Device Component
-----------------

Device components are the typical use case of a component. They encapsulate a
device and any adapters for that device.

.. figure:: ../../images/tickit-device-component.svg
    :align: center


(See `DeviceComponent`.)


System Component
-----------------

System components are themselves entire tickit simulations. They
contain their own device components and a scheduler for orchestrating
them. However, the scheduler in a system component acts as a nested scheduler
which is triggered by the master scheduler in the top level of the simulation
it belongs to.

.. figure:: ../../images/tickit-system-component.svg
    :align: center

System components can also contain their own system components
allowing for the construction of reasonably complex systems.

System components can be nested inside other components in the config so that
the master scheduler's wiring is correct, for example:

.. code-block:: yaml

    - type: examples.devices.trampoline.RandomTrampoline
      name: random_trampoline
      inputs: {}
      callback_period: 10000000000
    - type: tickit.core.components.system_component.SystemSimulation
      name: internal_tickit
      inputs:
        input_1:
          component: random_trampoline
          port: output
      components:
        - type: tickit.devices.sink.Sink
          name: internal_sink
          inputs:
            sink_1:
              component: external
              port: input_1
        - type: examples.devices.remote_controlled.RemoteControlled
          name: internal_tcp_controlled
          inputs: {}
      expose:
        output_1:
          component: internal_tcp_controlled
          port: observed
    - type: tickit.devices.sink.Sink
      name: external_sink
      inputs:
        sink_1:
          component: internal_tickit
          port: output_1

(See `SystemComponent`.)

The Overall Simulation
-------------------------------

A simulation containing both types of component will look something like this:

.. figure:: ../../images/tickit-overview-with-system-component.svg
    :align: center



.. _DeviceComponent: <tickit.core.components.device_component.DeviceComponent>
.. _SystemComponent: <tickit.core.components.system_component.SystemComponent>
