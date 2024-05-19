import numpy as np

from pyMRI.config import MRIConfig
from pyMRI.data_loading import ScanConfig, load_scan

from arcade import Window, SpriteSolidColor, SpriteList, camera


SPRITE_SIZE = 8


class MRIWindow(Window):

    def __init__(self, mri_config: MRIConfig, scan_config: ScanConfig):
        super().__init__(mri_config.screen_width, mri_config.screen_height, "Prospa 3D MRI visualiser")
        self.mri_config: MRIConfig = mri_config
        self.scan_config: ScanConfig = scan_config

        self._camera = camera.Camera2D(position=(0.0, 0.0))

        self._scan_images = load_scan(mri_config, scan_config)

        self._current_image: int = 0

        self._grid_sprites: SpriteList = SpriteList()
        self._grid: dict[tuple[int, int], SpriteSolidColor] = dict()
        for x in range(scan_config.phase_1_count):
            for y in range(scan_config.read_count):
                sprite = SpriteSolidColor(SPRITE_SIZE, SPRITE_SIZE, -(x + 0.5) * SPRITE_SIZE - (SPRITE_SIZE * scan_config.phase_1_count) - 10, (y + 0.5) * SPRITE_SIZE)
                self._grid[(x, y)] = sprite
                self._grid_sprites.append(sprite)

        self._dirty = True

    def colour_sprites(self):
        self._dirty = False

        data = np.fft.fftshift(np.fft.ifft2(np.fft.ifftshift(self._scan_images[self._current_image], axes=[-2, -1]), norm='ortho'), axes=[-2, -1])
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
        o_pos = self._camera.position
        self._camera.position = o_pos[0] - dx, o_pos[1] - dy

    def on_draw(self):
        self.clear()
        if self._dirty:
            self.colour_sprites()

        with self._camera.activate():
            self._grid_sprites.draw()
