from tickit.core.typedefs import ComponentID


def valid_device_id(device_id: ComponentID) -> None:
    if not device_id:
        raise ValueError


def output_topic(device_id: ComponentID) -> str:
    valid_device_id(device_id)
    return "tickit-" + device_id + "-out"


def input_topic(device_id: ComponentID) -> str:
    valid_device_id(device_id)
    return "tickit-" + device_id + "-in"
