from pyMRI.config import LaunchConfig
from pyMRI.data_loading import ScanConfig
from pyMRI.windowing.window import MRIWindow


def launch(config: LaunchConfig):
    win = MRIWindow(config)
    win.run()
