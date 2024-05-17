from pyMRI.config import MRIConfig

from arcade import Window


class MRIWindow(Window):

    def __init__(self, config: MRIConfig):
        super().__init__(config.screen_width, config.screen_height, "Prospa 3D MRI visualiser")
        self.mri_config: MRIConfig = config
