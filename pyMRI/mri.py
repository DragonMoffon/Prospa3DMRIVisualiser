import numpy as np

from pyMRI.config import MRIConfig
from pyMRI.data_loading import ScanConfig


class MRI:

    def __init__(self):
        self._original_mri: MRIConfig = None
        self._mri_config: MRIConfig = None

        self._original_scan: ScanConfig = None
        self._scan_config: ScanConfig = None

        self._raw_read_data: np.ndarray = None

    @property
    def mri_config(self):
        return self._mri_config

    @property
    def scan_config(self):
        return self._scan_config

    # File
    def open_file_dialog(self):
        if self._mri_config is not None:
            print()

    def load_file(self, src: str):
        pass

    # Processing Operations

    # Filtering Operations

    # Visual Operations

    # Camera Operations

