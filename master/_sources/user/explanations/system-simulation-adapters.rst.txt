System Simulation Adapters
==========================

Adapters may also be used with system simulations (`SystemComponent`),
as well as with devices (`DeviceComponent`). This would allow you, for example, to
query what device components are inside the system simulation component, and how they
are wired together.

Currently system adapters need both wiring and components. There is a helper base class
for implementing this.  

.. code-block:: python
        
    class BaseSystemSimulationAdapter:
        """A base for a SystemComponent adapter."""

        _components: Dict[ComponentID, Component]
        _wiring: Union[Wiring, InverseWiring]

        def setup_adapter(
            self,
            components: Dict[ComponentID, Component],
            wiring: Union[Wiring, InverseWiring],
        ) -> None:
            """Provides the components and wiring of a SystemComponent."""
            self._components = components
            self._wiring = wiring



Nested Amplifier Example
------------------------

The following system adapter is a simple ``CommandAdapter``. This Can be used to query the
SystemComponent for a list of ID's of the components it contains; and to
return the wiring map of the components.

.. code-block:: python

    class SystemSimulationAdapter(BaseSystemSimulationAdapter, CommandAdapter):

        _byte_format: ByteFormat = ByteFormat(b"%b\r\n")

        @RegexCommand(r"ids", False, "utf-8")
        async def get_component_ids(self) -> bytes:
            """Returns a list of ids for all the components in the system simulation."""
            return str(self._components.keys()).encode("utf-8")

        @RegexCommand(r"wiring", False, "utf-8")
        async def get_wiring(self) -> bytes:
            """Returns the wiring object used by the nested scheduler."""
            return str(self._wiring).encode("utf-8")

To use this adapter we would need to put it in an adapter container with ``TcpIo`` and
assign it as an argument in the SystemComponent.

.. code-block:: python

    @pydantic.v1.dataclasses.dataclass
    class NestedAmplifierWithAdapter(ComponentConfig):
        """Simulation of a nested amplifier with a CommandAdapter."""

        name: ComponentID
        inputs: Dict[PortID, ComponentPort]
        components: List[ComponentConfig]
        expose: Dict[PortID, ComponentPort]

        def __call__(self) -> Component:  # noqa: D102
            return SystemComponent(
                name=self.name,
                components=self.components,
                expose=self.expose,
                adapter=AdapterContainer(
                    SystemSimulationAdapter(),
                    TcpIo(host="localhost", port=25560),
                ),
            )



This ComponentConfig ``NestedAmplifierWithAdapter`` can be used as any other component.

Below is a very simple simulation with a system simulation component. It is a
source, which is connected to a `SystemComponent` which only contains a
single amplifier. The output of this amplfier is fed to the output of the system
simulation component, which is wired to a sink. 


.. code-block:: yaml

  - type: tickit.devices.source.Source
    name: source
    inputs: {}
    value: 10.0
  - type: examples.adapters.system_simulation_adapter_config.NestedAmplifierWithAdapter
    name: nested-amp
    inputs:
        input_1:
        component: source
        port: value
    components:
        - type: examples.devices.amplifier.Amplifier
        name: amp
        inputs:
            initial_signal:
            component: external
            port: input_1
        initial_amplification: 2
    expose:
        output_1:
        component: amp
        port: amplified_signal
  - type: tickit.devices.sink.Sink
    name: external_sink
    inputs:
        sink_1:
        component: nested-amp
        port: output_1



Interacting with devices using a system simulation adapter
----------------------------------------------------------

When using a system adapter you must be careful to achieve the behaviour you desire.

If you wish to write to and change the devices within the system simulation then any
change you make must be followed by raising an interrupt in that specific device
component. If you do not, the changes will not propagate correctly.

This is done below in the ``raise_component_interrupt`` method which takes a given
component ID and does ``await component.raise_interrupt()`` for the specific component.


.. code-block:: python

    class SystemSimulationAdapter(BaseSystemSimulationAdapter, CommandAdapter):

        _byte_format: ByteFormat = ByteFormat(b"%b\r\n")

        @RegexCommand(r"interrupt=(\w+)", False, "utf-8")
            async def raise_component_interrupt(self, id: str) -> bytes:
                """Raises an interrupt in the component of the given id."""
                component = self._components.get(ComponentID(id), None)

                if isinstance(component, BaseComponent):
                    await component.raise_interrupt()
                    return str(f"Raised Interupt in {component.name}").encode("utf-8")
                else:
                    return str("ComponentID not recognised, No interupt raised.").encode(
                        "utf-8"
                    )
