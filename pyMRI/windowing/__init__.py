from pyMRI.config import LaunchConfig
from pyMRI.windowing.window import Window


def launch(config: LaunchConfig):
    win = Window(config)
    win.run()
