import numpy as np

from pyMRI.config import MRIConfig
from pyMRI.data_loading import ScanConfig, load_scan

from pyMRI.rendering.fly_around_grip import FlyAroundGrip
from pyMRI.rendering.voxel import VoxelRenderer, Mode

from pyMRI.gui.menu import GuiMenu

from arcade import Window, SpriteSolidColor, SpriteList, camera, key

SPRITE_SIZE = 8


class MRIWindow(Window):

    def __init__(self, mri_config: MRIConfig, scan_config: ScanConfig):
        super().__init__(mri_config.screen_width, mri_config.screen_height, "Prospa 3D MRI visualiser")
        self.mri_config: MRIConfig = mri_config
        self.scan_config: ScanConfig = scan_config

        self._camera_2d = camera.Camera2D(position=(0.0, 0.0))

        self._camera = camera.PerspectiveProjector()
        self._camera.projection.far = 1000.0
        self._camera.view.position = (0.0, 0.0, -40.0)
        self._grip = FlyAroundGrip(self._camera.view)
        self._grip.toggle()

        self._scan_images = load_scan(mri_config, scan_config)
        self._scan_data = np.zeros([scan_config.phase_2_count, scan_config.phase_1_count, scan_config.read_count], dtype=np.complexfloating)
        for idx in range(0, scan_config.phase_2_count):
            img = self._scan_images[idx]
            self._scan_data[idx] = np.fft.fftshift(np.fft.ifft2(np.fft.ifftshift(img, axes=[-2, -1]), norm='ortho'), axes=[-2, -1])

        self._current_image: int = 0

        self._grid_sprites: SpriteList = SpriteList()
        self._grid_sprites.program = self.ctx.sprite_list_program_no_cull
        self._grid: dict[tuple[int, int], SpriteSolidColor] = dict()
        for x in range(scan_config.phase_1_count):
            for y in range(scan_config.read_count):
                sprite = SpriteSolidColor(SPRITE_SIZE, SPRITE_SIZE, -(x + 0.5) * SPRITE_SIZE, (y + 0.5) * SPRITE_SIZE)
                self._grid[(x, y)] = sprite
                self._grid_sprites.append(sprite)

        self._dirty = True

        self._renderer = VoxelRenderer(mri_config, scan_config, self._scan_data, self._camera, Mode.MAGNITUDE)
        self._gui_menu = GuiMenu()

    def colour_sprites(self):
        self._dirty = False

        data = self._scan_data[self._current_image]
        data = np.abs(data)
        greatest = np.max(data)
        data = data / greatest

        for x in range(self.scan_config.phase_1_count):
            for y in range(self.scan_config.read_count):
                c = int(255 * data[x, y])
                self._grid[(x, y)].color = (c, c, c, 255)

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        self._current_image = min(max(self._current_image + int(scroll_y), 0), self.scan_config.phase_2_count-1)
        self._dirty = True

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons, modifiers):
        o_pos = self._camera_2d.position
        self._camera_2d.position = o_pos[0] - dx, o_pos[1] - dy

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == key.GRAVE:
            self._grip.toggle()

    def on_draw(self):
        self.clear()
        if self._dirty:
            self.colour_sprites()

        self._renderer.draw()

        self._gui_menu.draw()