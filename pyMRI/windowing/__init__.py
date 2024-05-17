from pyMRI.config import MRIConfig
from pyMRI.windowing.window import MRIWindow


def launch(config: MRIConfig):
    win = MRIWindow(config)
    win.run()
