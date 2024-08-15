import numpy as np

import imgui
import imgui.integrations.pyglet as imgui_integration

from pyMRI.config import LaunchConfig
from pyMRI.mri import MRI

from pyMRI.rendering.camera import CameraCarousel
from pyMRI.rendering.voxel import VoxelRenderer

from pyMRI.gui.menu import GuiMenu
from pyMRI.gui.colouring import ColouringTab
# from pyMRI.gui.processing import ProcessingTab

from pyMRI.gui.warning import GuiWarning, WarningMode

from arcade import Window, key, Text, get_screens

SPRITE_SIZE = 8


class MRIWindow(Window):

    def __init__(self, launch_config: LaunchConfig):
        w, h = launch_config.screen_width, launch_config.screen_height
        if launch_config.fullscreen:
            scr = get_screens()[0]
            w, h = scr.width, scr.height
        super().__init__(w, h, launch_config.window_name, fullscreen=launch_config.fullscreen)
        self.center_window()
        imgui.create_context()
        imgui.get_io().fonts.get_tex_data_as_rgba32()

        self._switch_text = Text("Press ` or ~ to toggle menu", 10, 10, font_size=12)

        self._imgui_renderer = imgui_integration.create_renderer(self)

        self._carousel: CameraCarousel = CameraCarousel()

        self._voxel_renderer: VoxelRenderer = VoxelRenderer(self._carousel.projector)

        self._mri: MRI = MRI(launch_config, self._voxel_renderer)

        self._menu: GuiMenu = GuiMenu((ColouringTab(self._voxel_renderer),))

        self._warning_dialogs: list[GuiWarning] = []

        self._carousel.disable()
        self._menu.enable()
        self.set_exclusive_mouse(False)

        self._mri.initialise()

    def push_warning(self, warning: GuiWarning):
        self._warning_dialogs.append(warning)
        self.set_exclusive_mouse(False)
        self._menu.disable()
        self._carousel.disable()

    def pop_warning(self):
        self._warning_dialogs.pop(-1)
        if not self._warning_dialogs:
            self.set_exclusive_mouse(False)
            self._menu.enable()
            self._carousel.disable()

    def on_key_press(self, symbol: int, modifiers: int):
        if self._warning_dialogs:
            return

        if symbol == key.GRAVE:
            if self._carousel.is_disabled:
                self._carousel.enable()
                self._menu.disable()
                self.set_exclusive_mouse(True)
            else:
                self._carousel.disable()
                self._menu.enable()
                self.set_exclusive_mouse(False)

    def update_gui(self):
        self._imgui_renderer.process_inputs()
        imgui.new_frame()
        if self._warning_dialogs:
            self._warning_dialogs[-1].update()
        else:
            self._menu.update()
        imgui.end_frame()

    def draw_gui(self):
        imgui.render()
        self._imgui_renderer.render(imgui.get_draw_data())

    def on_update(self, delta_time: float):
        self.update_gui()

    def on_draw(self):
        self.clear()

        self._carousel.use()
        self._voxel_renderer.draw()

        self.default_camera.use()
        self.draw_gui()

        if not self._menu.is_disabled:
            self._switch_text.draw()
