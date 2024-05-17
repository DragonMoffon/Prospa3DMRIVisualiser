from pyMRI.config import MRIConfig
from pyMRI.data_loading import ScanConfig
from pyMRI.windowing.window import MRIWindow


def launch(mri_config: MRIConfig, scan_config: ScanConfig):
    win = MRIWindow(mri_config, scan_config)
    win.run()
