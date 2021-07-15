from collections import deque
from typing import Dict, Iterable, List, NewType, Set, Tuple

from tickit.core.typedefs import DeviceID, Input, IoId, Output
from tickit.utils.compat.functools import cached_property

Wiring = NewType("Wiring", Dict[DeviceID, Dict[IoId, Iterable[Tuple[DeviceID, IoId]]]])


class EventRouter:
    def __init__(self, wiring: Wiring) -> None:
        self.wiring = wiring

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
        inverse_tree = {dev: set() for dev in self.devices}
        for dev, deps in self.device_tree.items():
            for dep in deps:
                inverse_tree[dep].add(dev)
        return inverse_tree

    def dependants(self, root: DeviceID) -> Set[DeviceID]:
        dependants = set()
        to_crawl = deque([root])
        while to_crawl:
            dev = to_crawl.popleft()
            if dev in dependants:
                continue
            dependants.add(dev)
            if dev in self.device_tree.keys():
                to_crawl.extend(self.device_tree[dev] - dependants)
        return dependants

    def route(self, output: Output) -> List[Input]:
        inputs: List[Input] = list()
        for out_id, out_val in output.changes.items():
            for in_dev, _ in self.wiring[output.source][out_id]:
                inputs.append(Input(in_dev, output.time, {out_id: out_val}))
        return inputs
