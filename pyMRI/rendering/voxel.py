from array import array
from struct import pack
from enum import Enum
from math import radians, tan

from importlib.resources import read_text, path
import pyMRI.rendering.shaders as shaders

import numpy as np

from arcade import get_window
from arcade.camera import PerspectiveProjector
import arcade.gl as gl

from pyMRI.config import MRIConfig
from pyMRI.data_loading import ScanConfig, interpolate_scan


class Mode(Enum):
    MAGNITUDE = 0
    REAL = 1
    IMAG = 2


_BUFFER_HEADER_SIZE = 6 * 4  # 6 floats / ints


class VoxelRenderer:

    def __init__(self, mri_config: MRIConfig, scan_config: ScanConfig, raw_data: np.ndarray[..., np.dtype[np.complexfloating]], projector: PerspectiveProjector, mode: Mode = Mode.MAGNITUDE):
        self._win = win = get_window()
        self._ctx = ctx = win.ctx
        self._mri: MRIConfig = mri_config
        self._scan: ScanConfig = scan_config
        self._projector: PerspectiveProjector = projector
        self._mode: Mode = mode
        self._raw_data: np.ndarray[..., np.dtype[np.complexfloating]] = raw_data
        self._point_data: np.ndarray[..., np.dtype[np.float64]] = None
        self._point_buffer: gl.Buffer = ctx.buffer(reserve=(_BUFFER_HEADER_SIZE + 4 * scan_config.read_count * scan_config.phase_1_count * scan_config.phase_2_count))

        with path(shaders, 'gradient_rainbow.png') as p: self._density_gradient: gl.Texture2D = ctx.load_texture(p)
        print(self._density_gradient.components)

        self._dda_shader = ctx.program(
            vertex_shader=read_text(shaders, 'fullscreen_dda3d_vs.glsl'),
            fragment_shader=read_text(shaders, 'fullscreen_dda3d_fs.glsl')
        )
        self._dda_shader['emission_strength'] = 0.05

        self._dda_geometry = ctx.geometry(
            content=[
                gl.BufferDescription(
                    buffer=ctx.buffer(data=array('f', (-1.0, -1.0, -1.0, 1.0, 1.0, -1.0, 1.0, 1.0))),
                    formats='2f',
                    attributes=['in_pos']
                )
            ],
            mode=ctx.TRIANGLE_STRIP
        )

        self._process_data()

    def _process_data(self):
        match self._mode:
            case Mode.MAGNITUDE:
                self._point_data = abs(self._raw_data)
            case Mode.REAL:
                self._point_data = self._raw_data * (1+0j)
            case Mode.IMAG:
                self._point_data = self._raw_data * (0-1j)

        scn_cfg, linear_data = interpolate_scan(self._mri, self._scan, self._point_data)

        linear_data = np.reshape(linear_data, -1)
        linear_data = linear_data / np.max(linear_data)

        print(self._scan.read_count, self._scan.phase_1_count, self._scan.phase_2_count)
        print(scn_cfg.read_count, scn_cfg.phase_1_count, scn_cfg.phase_2_count)

        byte_data = pack(f'i i i f f f {len(linear_data)}f', scn_cfg.read_count, scn_cfg.phase_1_count, scn_cfg.phase_2_count, scn_cfg.read_FOV, scn_cfg.phase_1_FOV, scn_cfg.phase_2_FOV, *linear_data)
        self._point_buffer.write(byte_data)

    def update_raw_data(self, new_data: np.ndarray[..., np.dtype[np.complexfloating]]):
        self._raw_data = new_data
        self._process_data()

    def get_histogram(self):
        scn_cfg, linear_data = interpolate_scan(self._mri, self._scan, self._point_data)
        return np.histogram(linear_data, bins=max(1, int(np.max(self._point_data) - np.min(self._point_data)) // 4))

    def draw(self):
        # figure out the h_size of
        zoom = self._projector.view.zoom
        projection = self._projector.projection
        y = projection.near * tan(radians(projection.fov) / (2.0 * zoom))
        x = projection.aspect * y

        self._dda_shader['camera_data'] = x, y, projection.near
        self._dda_shader['inv_view'] = ~self._projector.generate_view_matrix()
        self._density_gradient.use(0)

        old_func = self._win.ctx.blend_func
        self._win.ctx.blend_func = self._win.ctx.BLEND_DEFAULT

        self._point_buffer.bind_to_storage_buffer()
        self._dda_geometry.render(self._dda_shader)

        self._win.ctx.blend_func = old_func

    @property
    def emission(self):
        return self._dda_shader['emission_strength']

    @emission.setter
    def emission(self, new_emission):
        self._dda_shader['emission_strength'] = new_emission
