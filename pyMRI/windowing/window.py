import numpy as np

import imgui
import imgui.integrations.pyglet as imgui_integration

from pyMRI.config import LaunchConfig
from pyMRI.mri import MRI

from pyMRI.rendering.camera import CameraCarousel
from pyMRI.rendering.voxel import VoxelRenderer, Mode

from pyMRI.gui.menu import GuiMenu
from pyMRI.gui.colouring import ColouringTab
from pyMRI.gui.processing import ProcessingTab

from pyMRI.gui.warning import GuiWarning, WarningMode

from arcade import Window, key, Text

SPRITE_SIZE = 8


class MRIWindow(Window):

    def __init__(self, launch_config: LaunchConfig):
        super().__init__(launch_config.screen_width, launch_config.screen_height, launch_config.window_name)
        imgui.create_context()
        imgui.get_io().display_size = self.width // 4, self.height // 4
        imgui.get_io().fonts.get_tex_data_as_rgba32()

        self._switch_text = Text("Press ` or ~ to toggle menu", 10, 10, font_size=12)

        self._imgui_renderer = imgui_integration.create_renderer(self)

        self._carousel: CameraCarousel = CameraCarousel()

        self._voxel_renderer: VoxelRenderer = None

        self._mri: MRI = None

        self._menu: GuiMenu = None

        self._scan_images = load_scan(mri_config, scan_config)
        self._scan_data = np.fft.ifftshift(self._scan_images, [-2])
        # for idx in range(0, scan_config.phase_2_count):
        #    img = self._scan_images[idx]
        #    # self._scan_data[idx] = img
        #    self._scan_data[idx] = np.fft.fftshift(np.fft.ifft2(np.fft.ifftshift(img, axes=[-2, -1]), norm='ortho'), axes=[-2, -1])
        #    # self._scan_data[idx] = np.fft.ifft2(img, norm='ortho')

        self._renderer = VoxelRenderer(mri_config, scan_config, self._scan_data, self._carousel.projector, Mode.MAGNITUDE)
        self._gui_menu = GuiMenu((ProcessingTab(self._renderer, mri_config, scan_config), ColouringTab(self._renderer),))

        self._warning_dialogs: list[GuiWarning] = []

        self._carousel.disable()
        self._gui_menu.enable()
        self.set_exclusive_mouse(False)

        self.push_warning(GuiWarning(self._imgui_renderer, "TEST", "Awogaaa", WarningMode.ERROR, continue_callback=lambda: print("YOOOO")))

    def push_warning(self, warning: GuiWarning):
        self._warning_dialogs.append(warning)
        self.set_exclusive_mouse(True)
        self._gui_menu.disable()
        self._carousel.disable()

    def pop_warning(self):
        self._warning_dialogs.pop(-1)
        if not self._warning_dialogs:
            self.set_exclusive_mouse(False)
            self._gui_menu.enable()
            self._carousel.disable()

    def on_key_press(self, symbol: int, modifiers: int):
        if self._warning_dialogs:
            return

        if symbol == key.GRAVE:
            if self._carousel.is_disabled:
                self._carousel.enable()
                self._gui_menu.disable()
                self.set_exclusive_mouse(True)
            else:
                self._carousel.disable()
                self._gui_menu.enable()
                self.set_exclusive_mouse(False)

    def update_gui(self):
        self._imgui_renderer.process_inputs()
        imgui.new_frame()
        if self._warning_dialogs:
            self._warning_dialogs[-1].update()
            if self._warning_dialogs[-1].is_popped:
                self.pop_warning()
        else:
            self._gui_menu.update()
        imgui.end_frame()

    def draw_gui(self):
        imgui.render()
        self._imgui_renderer.render(imgui.get_draw_data())

    def on_update(self, delta_time: float):
        self.update_gui()

    def on_draw(self):
        self.clear()

        self._carousel.use()
        self._renderer.draw()

        self.default_camera.use()
        self.draw_gui()

        if not self._gui_menu.is_disabled:
            self._switch_text.draw()
