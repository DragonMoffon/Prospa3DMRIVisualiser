from array import array

import imgui

from pyMRI.rendering.voxel import VoxelRenderer
from pyMRI.gui.tab import GuiTab


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

    def draw(self):
        if self._data_histogram is None:
            self._data_histogram = self._renderer.get_histogram()

        imgui.push_item_width(-1)
        x, _ = imgui.get_content_region_available()
        imgui.plot_histogram(
            "##histogram",
            array('f', self._data_histogram[0]),
            graph_size=(x, 80)

        )
        imgui.pop_item_width()
        _, self._renderer.density_scalar = imgui.slider_float("Density Scalar", self._renderer.density_scalar, 0.001, 1.0)
        _, self._renderer.emission_brightness = imgui.slider_float("Emission Brightness", self._renderer.emission_brightness, 0.001, 1.0)

