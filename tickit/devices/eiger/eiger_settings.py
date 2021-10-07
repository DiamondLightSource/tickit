from dataclasses import dataclass, field
from typing import Dict, List

from .eiger_schema import (
    FLOAT_GRID,
    UINT_GRID,
    field_config,
    ro_float,
    ro_str,
    rw_bool,
    rw_float,
    rw_int,
    rw_str,
)

FRAME_WIDTH: int = 4148
FRAME_HEIGHT: int = 4362

KA_ENERGIES: Dict[str, float] = {
    "Li": 54.3,
    "Be": 108.5,
    "B": 183.3,
    "C": 277.0,
    "N": 392.4,
    "O": 524.9,
    "F": 676.8,
    "Ne": 848.6,
    "Na": 1040.98,
    "Mg": 1253.6,
    "Al": 1486.7,
    "Si": 1739.98,
    "P": 2013.7,
    "S": 2307.84,
    "Cl": 2622.39,
    "Ar": 2957.7,
    "K": 3313.8,
    "Ca": 3691.68,
    "Sc": 4090.6,
    "Ti": 4510.84,
    "V": 4952.2,
    "Cr": 5414.72,
    "Mn": 5898.75,
    "Fe": 6403.84,
    "Co": 6930.32,
    "Ni": 7478.15,
    "Cu": 8047.78,
    "Zn": 8638.86,
}


@dataclass
class EigerSettings:
    """A data container for Eiger device configuration."""

    auto_summation: bool = field(default=True, metadata=rw_bool())
    beam_center_x: float = field(default=0.0, metadata=rw_float())
    beam_center_y: float = field(default=0.0, metadata=rw_float())
    bit_depth_image: int = field(default=16, metadata=rw_int())
    bit_depth_readout: int = field(default=16, metadata=rw_int())
    chi_increment: float = field(default=0.0, metadata=rw_float())
    chi_start: float = field(default=0.0, metadata=rw_float())
    compression: str = field(
        default="bslz4", metadata=rw_str(allowed_values=["bslz4", "lz4"])
    )
    # count_time: Dict[str, object] = field(
    #     default_factory=lambda: {
    #         "min": 0.000002999900061695371,
    #         "max": 1800,
    #         "value": 0.5,
    #         "value_type": "float",
    #         "access_mode": "rw",
    #         "unit": "s",
    #     }
    # )
    count_time: float = field(default=0.1, metadata=rw_float())
    countrate_correction_applied: bool = field(default=True, metadata=rw_bool())
    countrate_correction_count_cutoff: int = field(default=1000, metadata=rw_int())
    data_collection_date: str = field(
        default="2021-30-09T16:30:00.000-01:00", metadata=ro_str()
    )
    description: str = field(
        default="Simulated Eiger X 16M Detector", metadata=ro_str()
    )
    detector_distance: float = field(default=2.0, metadata=rw_float())
    detector_number: str = field(default="EIGERSIM001", metadata=ro_str())
    detector_readout_time: float = field(default=0.01, metadata=rw_float())
    element: str = field(default="Oganesson", metadata=rw_str())
    flatfield: List[List[float]] = field(
        default_factory=lambda: [[]], metadata=field_config(value_type=FLOAT_GRID)
    )
    flatfield_correction_applied: bool = field(default=True, metadata=rw_bool())
    frame_time: float = field(default=0.12, metadata=rw_float())
    kappa_increment: float = field(default=0.0, metadata=rw_float())
    kappa_start: float = field(default=0.0, metadata=rw_float())
    nimages: int = field(default=1, metadata=rw_int())
    ntrigger: int = field(default=1, metadata=rw_int())
    number_of_excuded_pixels: int = field(default=0, metadata=rw_int())
    omega_increment: float = field(default=0.0, metadata=rw_float())
    omega_start: float = field(default=0.0, metadata=rw_float())
    phi_increment: float = field(default=0.0, metadata=rw_float())
    phi_start: float = field(default=0.0, metadata=rw_float())
    photon_energy: float = field(default=8041.0, metadata=rw_float())
    pixel_mask: List[List[int]] = field(
        default_factory=lambda: [[]], metadata=field_config(value_type=UINT_GRID)
    )
    pixel_mask_applied: bool = field(default=False, metadata=rw_bool())
    roi_mode: str = field(
        default="disabled", metadata=rw_str(allowed_values=["disabled", "4M"])
    )
    sensor_material: str = field(default="Silicon", metadata=ro_str())
    sensor_thickness: float = field(default=0.01, metadata=ro_float())
    software_version: str = field(default="0.1.0", metadata=ro_str())
    threshold_energy: float = field(default=4020.5, metadata=rw_float())
    trigger_mode: str = field(
        default="exts", metadata=rw_str(allowed_values=["exts", "ints", "exte", "inte"])
    )
    two_theta_increment: float = field(default=0.0, metadata=rw_float())
    two_theta_start: float = field(default=0.0, metadata=rw_float())
    wavelength: float = field(default=1e-9, metadata=rw_float())
    x_pixel_size: float = field(default=0.01, metadata=ro_float())
    x_pixels_in_detector: int = field(default=FRAME_WIDTH, metadata=rw_int())
    y_pixel_size: float = field(default=0.01, metadata=ro_float())
    y_pixels_in_detector: int = field(default=FRAME_HEIGHT, metadata=rw_int())

    # def set_element(self, element: str) -> bool:
    #     return hasattr(KA_ENERGIES, element)
