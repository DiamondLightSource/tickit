from collections import deque
from typing import DefaultDict, Dict, List, Optional, Set, Tuple, Union, overload

from tickit.core.typedefs import Changes, DeviceID, Input, IoId, Output
from tickit.utils.compat.functools_compat import cached_property

_Default_Wiring = DefaultDict[DeviceID, DefaultDict[IoId, Set[Tuple[DeviceID, IoId]]]]
_Wiring = Dict[DeviceID, Dict[IoId, Set[Tuple[DeviceID, IoId]]]]
_Default_InverseWiring = DefaultDict[DeviceID, DefaultDict[IoId, Tuple[DeviceID, IoId]]]
_Inverse_Wiring = Dict[DeviceID, Dict[IoId, Tuple[DeviceID, IoId]]]


class Wiring(_Default_Wiring):
    def __init__(self, wiring: Optional[_Wiring] = None,) -> None:
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


class InverseWiring(_Default_InverseWiring):
    def __init__(self, wiring: Optional[_Inverse_Wiring] = None,) -> None:
        _wiring = (
            {dev: DefaultDict(None, io) for dev, io in wiring.items()}
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


class EventRouter:
    _wiring: Wiring

    @overload
    def __init__(self, wiring: Wiring) -> None:
        ...

    @overload
    def __init__(self, wiring: InverseWiring) -> None:
        ...

    def __init__(self, wiring: Union[Wiring, InverseWiring]) -> None:
        if isinstance(wiring, Wiring):
            self._wiring = wiring
        elif isinstance(wiring, InverseWiring):
            self._wiring = Wiring.from_inverse_wiring(wiring)

    @cached_property
    def wiring(self) -> Wiring:
        return self._wiring

    @cached_property
    def devices(self) -> Set[DeviceID]:
        return set.union(self.input_devices, self.output_devices)

    @cached_property
    def output_devices(self) -> Set[DeviceID]:
        return set(self.wiring.keys())

    @cached_property
    def input_devices(self) -> Set[DeviceID]:
        return set(
            dev
            for out in self.wiring.values()
            for port in out.values()
            for dev, _ in port
        )

    @cached_property
    def device_tree(self) -> Dict[DeviceID, Set[DeviceID]]:
        return {
            dev: set(dev for port in out.values() for dev, _ in port)
            for dev, out in self.wiring.items()
        }

    @cached_property
    def inverse_device_tree(self) -> Dict[DeviceID, Set[DeviceID]]:
        inverse_tree: Dict[DeviceID, Set[DeviceID]] = {
            dev: set() for dev in self.input_devices
        }
        for dev, deps in self.device_tree.items():
            for dep in deps:
                inverse_tree[dep].add(dev)
        return inverse_tree

    def dependants(self, root: DeviceID) -> Set[DeviceID]:
        dependants = set()
        to_crawl = deque([root])
        while to_crawl:
            dev = to_crawl.popleft()
            if dev not in dependants:
                dependants.add(dev)
                if dev in self.device_tree.keys():
                    to_crawl.extend(self.device_tree[dev] - dependants)
        return dependants

    def route(self, output: Output) -> List[Input]:
        inputs: List[Input] = list()
        for out_id, out_val in output.changes.items():
            for in_dev, _ in self.wiring[output.source][out_id]:
                assert output.time is not None
                inputs.append(Input(in_dev, output.time, Changes({out_id: out_val})))
        return inputs
