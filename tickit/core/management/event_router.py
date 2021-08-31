from collections import deque
from typing import DefaultDict, Dict, List, Optional, Set, Tuple, Union, overload

from immutables import Map

from tickit.core.components.component import ComponentConfig
from tickit.core.typedefs import Changes, ComponentID, Input, IoId, Output
from tickit.utils.compat.functools_compat import cached_property

Default_Wiring_Struct = DefaultDict[
    ComponentID, DefaultDict[IoId, Set[Tuple[ComponentID, IoId]]]
]
Wiring_Struct = Dict[ComponentID, Dict[IoId, Set[Tuple[ComponentID, IoId]]]]
Default_InverseWiring_Struct = DefaultDict[
    ComponentID, DefaultDict[IoId, Tuple[ComponentID, IoId]]
]
Inverse_Wiring_Struct = Dict[ComponentID, Dict[IoId, Tuple[ComponentID, IoId]]]


class Wiring(Default_Wiring_Struct):
    def __init__(self, wiring: Optional[Wiring_Struct] = None,) -> None:
        _wiring = (
            {dev: DefaultDict(set, io) for dev, io in wiring.items()}
            if wiring
            else dict()
        )
        return super().__init__(lambda: DefaultDict(set, dict()), _wiring)

    @classmethod
    def from_inverse_wiring(cls, inverse_wiring: "InverseWiring") -> "Wiring":
        wiring: Wiring = cls()
        for in_dev, in_ios in inverse_wiring.items():
            for in_io, (out_dev, out_io) in in_ios.items():
                wiring[out_dev][out_io].add((in_dev, in_io))
        return wiring


class InverseWiring(Default_InverseWiring_Struct):
    def __init__(self, wiring: Optional[Inverse_Wiring_Struct] = None,) -> None:
        _wiring = (
            {dev: DefaultDict(None, io) for dev, io in wiring.items() if io}
            if wiring
            else dict()
        )
        return super().__init__(lambda: DefaultDict(None, dict()), _wiring)

    @classmethod
    def from_wiring(cls, wiring: Wiring) -> "InverseWiring":
        inverse_wiring: InverseWiring = cls()
        for out_dev, out_ids in wiring.items():
            for out_io, ports in out_ids.items():
                for in_dev, in_io in ports:
                    inverse_wiring[in_dev][in_io] = (out_dev, out_io)
        return inverse_wiring

    @classmethod
    def from_component_configs(cls, configs: List[ComponentConfig]):
        return cls({config.name: config.inputs for config in configs})


class EventRouter:
    _wiring: Wiring

    @overload
    def __init__(self, wiring: Wiring) -> None:
        pass

    @overload
    def __init__(self, wiring: InverseWiring) -> None:
        pass

    def __init__(self, wiring: Union[Wiring, InverseWiring]) -> None:
        if isinstance(wiring, Wiring):
            self._wiring = wiring
        elif isinstance(wiring, InverseWiring):
            self._wiring = Wiring.from_inverse_wiring(wiring)

    @cached_property
    def wiring(self) -> Wiring:
        return self._wiring

    @cached_property
    def components(self) -> Set[ComponentID]:
        return set.union(self.input_components, self.output_components)

    @cached_property
    def output_components(self) -> Set[ComponentID]:
        return set(self.wiring.keys())

    @cached_property
    def input_components(self) -> Set[ComponentID]:
        return set(
            dev
            for out in self.wiring.values()
            for port in out.values()
            for dev, _ in port
        )

    @cached_property
    def component_tree(self) -> Dict[ComponentID, Set[ComponentID]]:
        return {
            dev: set(dev for port in out.values() for dev, _ in port)
            for dev, out in self.wiring.items()
        }

    @cached_property
    def inverse_component_tree(self) -> Dict[ComponentID, Set[ComponentID]]:
        inverse_tree: Dict[ComponentID, Set[ComponentID]] = {
            dev: set() for dev in self.components
        }
        for dev, deps in self.component_tree.items():
            for dep in deps:
                inverse_tree[dep].add(dev)
        return inverse_tree

    def dependants(self, root: ComponentID) -> Set[ComponentID]:
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
        inputs: Set[Input] = set()
        for out_id, out_val in output.changes.items():
            for in_dev, in_id in self.wiring[output.source][out_id]:
                assert output.time is not None
                inputs.add(Input(in_dev, output.time, Changes(Map({in_id: out_val}))))
        return inputs
