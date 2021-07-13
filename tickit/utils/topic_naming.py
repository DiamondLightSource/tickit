from tickit.core.typedefs import DeviceID


def output_topic(device: DeviceID):
    return "tickit-" + device + "-out"


def input_topic(device: DeviceID):
    return "tickit-" + device + "-in"
