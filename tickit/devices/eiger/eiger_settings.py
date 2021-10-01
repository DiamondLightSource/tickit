from dataclasses import dataclass, field
from typing import Dict, List


# TODO: Figure out how to properly declare the 2d arrays for flatfield and pixel_mask,
# as they return 'None' when requesting.
@dataclass
class EigerSettings:
    """A data container for Eiger device configuration."""

    auto_summation: bool = True
    beam_center_x: float = 0.5
    beam_center_y: float = 0.5
    bit_depth_image: int = 32
    bit_depth_readout: int = 32
    chi_increment: float = 0.1
    chi_start: float = 0.1
    compression: str = "lz4"
    count_time: Dict[str, object] = field(
        default_factory=lambda: {
            "min": 0.000002999900061695371,
            "max": 1800,
            "value": 0.5,
            "value_type": "float",
            "access_mode": "rw",
            "unit": "s",
        }
    )
    countrate_correction_applied: bool = True
    countrate_correction_count_cutoff: int = 1
    data_collection_date: str = "30/9/2021"
    description: str = "Eiger X 16M"
    detector_distance: float = 1.0
    detector_number: str = "1234"
    detector_readout_time: float = 0.02
    element: str = "?"
    flatfield: List[List[float]] = field(
        default_factory=lambda: [[1.0] for i in range(1000)]
    )
    flatfield_correction_applied: bool = True
    frame_time: float = 100
    kappa_increment: float = 0.1
    kappa_start: float = 0.1
    nimages: int = 100
    ntrigger: int = 1
    number_of_excuded_pixels: int = 5
    omega_increment: float = 0.1
    omega_start: float = 0.1
    phi_increment: float = 0.1
    phi_start: float = 0.1
    photon_energy: float = 1.5
    pixel_mask: List[List[int]] = field(
        default_factory=lambda: [[1] for i in range(1000)]
    )
    pixel_mask_applied: bool = True
    roi_mode: str = "4M"
    sensor_material: str = "Al"
    sensor_thickness: float = 0.125
    software_version: str = "1.8"
    threshold_energy: float = 1.2
    trigger_mode: str = "External"
    two_theta_increment: float = 0.2
    two_theta_start: float = 0.2
    wavelength: float = 0.25
    x_pixel_size: float = 0.01
    x_pixels_in_detector: int = 1000
    y_pixel_size: float = 0.01
    y_pixels_in_detector: int = 1000
