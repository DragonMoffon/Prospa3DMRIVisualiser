import numpy as np
from enum import Enum

from pyMRI.config import MRIConfig
from pyMRI.data_loading import ScanConfig


class Mode(Enum):
    MAGNITUDE = 0
    REAL = 1
    IMAG = 2


class VoxelRenderer:

    def __init__(self, mri_config: MRIConfig, scan_config: ScanConfig, raw_data: np.ndarray[..., np.dtype[np.complexfloating]], mode: Mode = Mode.MAGNITUDE):
        self._mri: MRIConfig = mri_config
        self._scan: ScanConfig = scan_config
        self._mode: Mode = mode
        self._raw_data: np.ndarray[..., np.dtype[np.complexfloating]] = raw_data
        self._point_data: np.ndarray[..., np.dtype[np.float64]] = None



        self._process_data()

    def _process_data(self):
        match self._mode:
            case Mode.MAGNITUDE:
                self._point_data = abs(self._raw_data)
            case Mode.REAL:
                self._point_data = self._raw_data * (1+0j)
            case Mode.IMAG:
                self._point_data = self._raw_data * (0-1j)

    def update_raw_data(self, new_data: np.ndarray[..., np.dtype[np.complexfloating]]):
        self._point_data = new_data
        self._process_data()