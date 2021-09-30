from dataclasses import dataclass
from typing import List


@dataclass
class EigerConfig:
    """A data container for Eiger device configuration."""

    auto_summation: bool
    beam_center_x: float
    beam_center_y: float
    bit_depth_image: int
    bit_depth_readout: int
    chi_increment: float
    chi_start: float
    compression: str
    count_time: float
    countrate_correction_applied: bool
    countrate_correction_count_cutoff: int
    data_collection_date: str
    description: str
    detector_distance: float
    detector_number: str
    detector_readout_time: float
    element: str
    flatfield: List[List[float]]
    flatfield_correction_applied: bool
    frame_time: float
    kappa_increment: float
    kappa_start: float
    nimages: int
    ntrigger: int
    number_of_excuded_pixels: int
    omega_increment: float
    omega_start: float
    phi_increment: float
    phi_start: float
    photon_energy: float
    pixel_mask: List[List[int]]
    pixel_mask_applied: bool
    roi_mode: str
    sensor_material: str
    sensor_thickness: float
    software_version: str
    threshold_energy: float
    trigger_mode: str
    two_theta_increment: float
    two_theta_start: float
    wavelength: float
    x_pixel_size: float
    x_pixels_in_detector: int
    y_pixel_size: float
    y_pixels_in_detector: int
