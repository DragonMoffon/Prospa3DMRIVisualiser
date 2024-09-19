from imgui_bundle import imgui
from pyMRI._distutil_workaround import PygletProgrammablePipelineRenderer

from pyMRI.config import LaunchConfig
from pyMRI.mri import MRI

from pyMRI.rendering.camera import CameraCarousel
from pyMRI.rendering.voxel import VoxelRendererOld as VoxelRenderer

from pyMRI.gui.gui import GUI

from arcade import Window as ArcadeWindow, key, Text, get_screens

SPRITE_SIZE = 8


class Window(ArcadeWindow):

    def __init__(self, launch_config: LaunchConfig):
        w, h = launch_config.screen_width, launch_config.screen_height
        if launch_config.fullscreen:
            scr = get_screens()[0]
            w, h = scr.width, scr.height
        super().__init__(
            w, h, launch_config.window_name, fullscreen=launch_config.fullscreen
        )
        GUI.initialise()
        self.center_window()

        self._switch_text = Text("Press ` or ~ to toggle menu", 10, 10, font_size=12)

        self._carousel: CameraCarousel = CameraCarousel()

        # self._voxel_renderer: VoxelRenderer = VoxelRenderer(self._carousel.projector)

        # self._mri: MRI = MRI(launch_config, self._voxel_renderer)

        # self._mri.initialise()

    def on_key_press(self, symbol: int, modifiers: int):
        if GUI.exclusive or GUI.capturing_input:
            pass

        if symbol == key.GRAVE:
            if GUI.show_menu:
                GUI.disable_menu()
            else:
                GUI.enable_menu()

    def on_update(self, delta_time: float):
        GUI.update()

    def on_draw(self):
        self.clear()

        with self._carousel.activate():
            pass
            # self._voxel_renderer.draw()

        with self.default_camera.activate():
            GUI.draw()

            if not GUI.exclusive:
                self._switch_text.draw()
