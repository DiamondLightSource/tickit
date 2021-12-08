from tickit.devices.eiger.data.schema import Header, ImageBlob
from tickit.devices.eiger.stream.stream_config import StreamConfig


def header(stream_config: StreamConfig) -> Header:
    # TODO: Implementation for flatfield etc.
    return Header(
        global_header={
            "header_detail": stream_config.header_detail,
            "htype": "dheader-1.0",
            "series": 4,
        },
        global_header_config=config_header(acq.eiger_config),
    )


def image_blob(acq: AcquisitionEvent, image: Image) -> ImageBlob:
    width = acq.eiger_config.x_pixels_in_detector
    height = acq.eiger_config.y_pixels_in_detector
    # TODO: Hard-coded bit_depth for now
    # bit_depth = acq.eiger_config.bit_depth_image
    image_size = len(image.data)
    return ImageBlob(
        header={
            "frame": image.index,
            "hash": image.hash,
            "htype": "dimage-1.0",
            "series": 4,
        },
        dimensions={
            "encoding": image.encoding,
            "htype": "dimage_d-1.0",
            "shape": [width, height],
            "size": image_size,
            "type": "uint16",
        },
        blob=image.data,
        times={"htype": "dconfig-1.0", "real_time": 0, "start_time": 0, "stop_time": 0},
    )


CONFIG_HEADER_KEYS = [
    "bit_depth_image",
    "bit_depth_readout",
    "compression",
    "count_time",
    "data_collection_date",
    "frame_time",
    "nimages",
    "ntrigger",
    "photon_energy",
    "sensor_material",
    "threshold_energy",
    "trigger_mode",
    "x_pixels_in_detector",
    "y_pixels_in_detector",
]


def config_header(config: EigerConfig):
    return {key: getattr(config, key) for key in CONFIG_HEADER_KEYS}
