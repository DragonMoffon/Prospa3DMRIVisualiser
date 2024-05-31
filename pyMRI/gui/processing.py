"""
orientation: 'zyx'
re-orient: #
pre-shift: # x, # y, # z
post-shift: # x, # y, # z
fft #
"""
import imgui

from pyMRI.rendering.voxel import VoxelRenderer
from pyMRI.gui.tab import GuiTab


"""class ProcessingTab(GuiTab):

    def __init__(self, voxel_renderer: VoxelRenderer, mri: MRIConfig, scan: ScanConfig):
        super().__init__("Processing")
        self._mri: MRIConfig = mri
        self._scan: ScanConfig = scan

        self._renderer: VoxelRenderer = voxel_renderer

    def update(self):
        pass
"""