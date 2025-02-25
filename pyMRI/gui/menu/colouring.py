import numpy as np

from imgui_bundle import imgui

from pyMRI.rendering.voxel import VoxelRenderer
from pyMRI.gui.menu.tab import GuiTab


class ColourTag:

    def __init__(self):
        self.colour = (255, 255, 255)
        self.density = 0
        self.width = 1


class ColouringTab(GuiTab):

    def __init__(self, voxel_renderer: VoxelRenderer):
        super().__init__("Colouring")
        self._renderer: VoxelRenderer = voxel_renderer
        self._data_histogram = None

        self._colours = []

    def update(self):
        if self._data_histogram is None:
            self._data_histogram = np.array([1.0], dtype=np.float32) #self._renderer.get_histogram()

        with imgui_ctx.push_item_width(-1):
            x, _ = imgui.get_content_region_avail()
            imgui.plot_histogram(
                "##histogram",
                self._data_histogram,
                graph_size=(x, 80)
            )

        _, self._renderer.density_scalar = imgui.slider_float("Density Scalar", self._renderer.density_scalar, 0.001, 1.0)
        _, self._renderer.emission_brightness = imgui.slider_float("Emission Brightness", self._renderer.emission_brightness, 0.001, 1.0)
