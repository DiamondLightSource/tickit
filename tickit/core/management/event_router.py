from collections import deque
from typing import DefaultDict, Dict, List, Optional, Set, Union, overload

from immutables import Map

from tickit.core.components.component import ComponentConfig
from tickit.core.typedefs import (
    Changes,
    ComponentID,
    ComponentPort,
    Input,
    Output,
    PortID,
)
from tickit.utils.compat.functools_compat import cached_property

#: A mapping of component output ports to component input ports with defaults
Default_Wiring_Struct = DefaultDict[
    ComponentID, DefaultDict[PortID, Set[ComponentPort]]
]
#: A mapping of component output ports to component input ports
Wiring_Struct = Dict[ComponentID, Dict[PortID, Set[ComponentPort]]]
#: A mapping of component input ports to component output ports with defaults
Default_InverseWiring_Struct = DefaultDict[
    ComponentID, DefaultDict[PortID, ComponentPort]
]
#: A mapping of component input ports to component output ports
Inverse_Wiring_Struct = Dict[ComponentID, Dict[PortID, ComponentPort]]


class Wiring(Default_Wiring_Struct):
    """A mapping of component output ports to component input ports with defaults

    A mapping of component output ports to component input ports, used to represent the
    connections between components in a system. Defaults are generated in case of
    missing mapping keys; for an unknown component, an empty output port mapping is
    created, whilst for an unknown output port an empty input port set is created
    """

    def __init__(self, wiring: Optional[Wiring_Struct] = None) -> None:
        """A constructor which adds defaults to a wiring struct if provided

        A constructor which adds defaults to a wiring struct if provided, otherwise an
        empty default dict is created

        Args:
            wiring (Optional[Wiring_Struct]): An optional wiring struct. Defaults to
                None.
        """
        _wiring = (
            {dev: DefaultDict(set, io) for dev, io in wiring.items()}
            if wiring
            else dict()
        )
        return super().__init__(lambda: DefaultDict(set, dict()), _wiring)

    @classmethod
    def from_inverse_wiring(cls, inverse_wiring: "InverseWiring") -> "Wiring":
        """An alternative constructor which un-inverts an inverse wiring struct"""
        wiring: Wiring = cls()
        for in_dev, in_ios in inverse_wiring.items():
            for in_io, (out_dev, out_io) in in_ios.items():
                wiring[out_dev][out_io].add(ComponentPort(in_dev, in_io))
        return wiring


class InverseWiring(Default_InverseWiring_Struct):
    """A mapping of component input ports to component output ports

    A mapping of component input ports to component output ports, used to represent the
    connections between components in a system. When either an unknown input component
    or an unknown input component port is requested a KeyError is raised.
    """

    def __init__(self, wiring: Optional[Inverse_Wiring_Struct] = None) -> None:
        """A constructor which adds defaults to an inverse wiring struct if provided

        A constructor which adds defaults to an inverse wiring struct if provided,
        otherwise an empty default dict is created

        Args:
            wiring (Optional[Inverse_Wiring_Struct]): An optional inverse wiring struct.
                Defaults to None.
        """
        _wiring = (
            {dev: DefaultDict(None, io) for dev, io in wiring.items() if io}
            if wiring
            else dict()
        )
        return super().__init__(lambda: DefaultDict(None, dict()), _wiring)

    @classmethod
    def from_wiring(cls, wiring: Wiring) -> "InverseWiring":
        """An alternative constructor which inverts a wiring struct"""
        inverse_wiring: InverseWiring = cls()
        for out_dev, out_ids in wiring.items():
            for out_io, ports in out_ids.items():
                for in_dev, in_io in ports:
                    inverse_wiring[in_dev][in_io] = ComponentPort(out_dev, out_io)
        return inverse_wiring

    @classmethod
    def from_component_configs(cls, configs: List[ComponentConfig]):
        """An alterantive constructor which creates the struct from a list of component configs

        Args:
            configs (List[ComponentConfig]): A list of component config data containers
        """
        return cls({config.name: config.inputs for config in configs})


class EventRouter:
    """A utility class responsible for routing changes between components"""

    _wiring: Wiring

    @overload
    def __init__(self, wiring: Wiring) -> None:
        pass

    @overload
    def __init__(self, wiring: InverseWiring) -> None:
        pass

    def __init__(self, wiring: Union[Wiring, InverseWiring]) -> None:
        """A constructor which un-inverts wiring if requred and stores for use in utilities

        Args:
            wiring (Union[Wiring, InverseWiring]): A wiring or inverse wiring object
                representing the connections between components in the system
        """
        if isinstance(wiring, Wiring):
            self._wiring = wiring
        elif isinstance(wiring, InverseWiring):
            self._wiring = Wiring.from_inverse_wiring(wiring)

    @cached_property
    def wiring(self) -> Wiring:
        """A cached property which returns the wiring used by the event router

        Returns:
            Wiring: The wiring used by the event router
        """
        return self._wiring

    @cached_property
    def components(self) -> Set[ComponentID]:
        """A cached property which returns a set of all components in the wiring

        Returns:
            Set[ComponentID]: A set of all components in the wiring
        """
        return set.union(self.input_components, self.output_components)

    @cached_property
    def output_components(self) -> Set[ComponentID]:
        """A cached property which returns a set of components which provide outputs

        Returns:
            Set[ComponentID]: A set of components which provide outputs
        """
        return set(self.wiring.keys())

    @cached_property
    def input_components(self) -> Set[ComponentID]:
        """A cached property which returns a set of components which recieve inputs

        Returns:
            Set[ComponentID]: A set of components which recieve inputs
        """
        return set(
            dev
            for out in self.wiring.values()
            for port in out.values()
            for dev, _ in port
        )

    @cached_property
    def component_tree(self) -> Dict[ComponentID, Set[ComponentID]]:
        """A cached property which returns a mapping of first order component dependants

        A cached property which returns a mapping of components to the set of
        components which are wired to any of its outputs

        Returns:
            Dict[ComponentID, Set[ComponentID]]:
                A mapping of components to the set of components which are wired to any
                of its outputs
        """
        return {
            dev: set(dev for port in out.values() for dev, _ in port)
            for dev, out in self.wiring.items()
        }

    @cached_property
    def inverse_component_tree(self) -> Dict[ComponentID, Set[ComponentID]]:
        """A cached property which returns a mapping of first order component dependancies

        A cached property which returns a mapping of components to the set of
        components which are wired to any of its inputs

        Returns:
            Dict[ComponentID, Set[ComponentID]]:
                A mapping of components to the set of components which are wired to any
                of its inputs
        """
        inverse_tree: Dict[ComponentID, Set[ComponentID]] = {
            dev: set() for dev in self.components
        }
        for dev, deps in self.component_tree.items():
            for dep in deps:
                inverse_tree[dep].add(dev)
        return inverse_tree

    def dependants(self, root: ComponentID) -> Set[ComponentID]:
        """A method with returns the recursive dependants of a component

        A method which returns a set of all components which are recursively dependant
        on the root component

        Args:
            root (ComponentID): The root component

        Returns:
            Set[ComponentID]:
                A set of all components which are recursively dependant on the root
                component
        """
        dependants = set()
        to_crawl = deque([root])
        while to_crawl:
            dev = to_crawl.popleft()
            if dev not in dependants:
                dependants.add(dev)
                if dev in self.component_tree.keys():
                    to_crawl.extend(self.component_tree[dev] - dependants)
        return dependants

    def route(self, output: Output) -> Set[Input]:
        """A method which generates a set of inputs which result from an output

        A method which generates a set of inputs which result from the propagation of
        an output according to the wiring

        Args:
            output (Output): The output to propagate

        Returns:
            Set[Input]:
                A set of inputs which result from the propagation of an output
                according to the wiring
        """
        inputs: Set[Input] = set()
        for out_id, out_val in output.changes.items():
            for in_dev, in_id in self.wiring[output.source][out_id]:
                assert output.time is not None
                inputs.add(Input(in_dev, output.time, Changes(Map({in_id: out_val}))))
        return inputs
