from pyMRI.config import MRIConfig
from pyMRI.data_loading import ScanConfig

from arcade import Window


class MRIWindow(Window):

    def __init__(self, mri_config: MRIConfig, scan_config: ScanConfig):
        super().__init__(mri_config.screen_width, mri_config.screen_height, "Prospa 3D MRI visualiser")
        self.mri_config: MRIConfig = mri_config
        self.scan_config: ScanConfig = scan_config
