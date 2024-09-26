from array import array
from struct import pack
from enum import Enum
from math import radians, tan, atan

from importlib.resources import read_text, path
import pyMRI.rendering.shaders as shaders

import numpy as np

from arcade import get_window
from arcade.camera import PerspectiveProjector
import arcade.gl as gl

from pyMRI.processing import COLOUR_STEP, RenderData, ORIENTATION_MAP


class Mode(Enum):
    MAGNITUDE = 0
    REAL = 1
    IMAG = 2


_BUFFER_HEADER_SIZE = 6 * 0b0100  # 6 floats / ints


class VoxelRendererOld:

    def __init__(self, projector: PerspectiveProjector):
        self._win = win = get_window()
        self._ctx = ctx = win.ctx
        self._projector: PerspectiveProjector = projector
        self._point_buffer: gl.Buffer = None

        with path(shaders, "gradient_rainbow.png") as p:
            self._density_gradient: gl.Texture2D = ctx.load_texture(p)

        self._dda_shader = ctx.program(
            vertex_shader=read_text(shaders, "fullscreen_dda3d_vs.glsl"),
            fragment_shader=read_text(shaders, "fullscreen_dda3d_fs.glsl"),
        )
        self.emission_brightness = 0.05
        self.density_scalar = 1.0

        self._dda_geometry = ctx.geometry(
            content=[
                gl.BufferDescription(
                    buffer=ctx.buffer(
                        data=array("f", (-1.0, -1.0, -1.0, 1.0, 1.0, -1.0, 1.0, 1.0))
                    ),
                    formats="2f",
                    attributes=["in_pos"],
                )
            ],
            mode=ctx.TRIANGLE_STRIP,
        )

    def update_gpu_data(self, data, data_config):
        """match self._mode:
        case Mode.MAGNITUDE:
            self._point_data = abs(self._raw_data)
        case Mode.REAL:
            self._point_data = self._raw_data * (1+0j)
        case Mode.IMAG:
            self._point_data = self._raw_data * (0-1j)"""

        linear_data = abs(data)

        linear_data = np.reshape(linear_data, -1)
        linear_data = linear_data / np.max(linear_data)

        _buffer_size = _BUFFER_HEADER_SIZE + len(linear_data) * 4
        if self._point_buffer is None:
            self._point_buffer = self._ctx.buffer(reserve=_buffer_size)
        elif self._point_buffer.size != _buffer_size:
            self._point_buffer.orphan(_buffer_size)

        byte_data = pack(
            f"i i i f f f {len(linear_data)}f",
            data_config.read_count,
            data_config.phase_1_count,
            data_config.phase_2_count,
            data_config.read_FOV,
            data_config.phase_1_FOV,
            data_config.phase_2_FOV,
            *linear_data,
        )
        self._point_buffer.write(byte_data)

    # TODO: move to MRI
    # return np.histogram(linear_data, bins=max(1, int(np.max(self._point_data) - np.min(self._point_data)) // 4))

    def draw(self):
        if self._point_buffer is None:
            return

        # figure out the h_size of
        zoom = self._projector.view.zoom
        projection = self._projector.projection
        y = projection.near * tan(radians(projection.fov) / (2.0 * zoom))
        x = projection.aspect * y

        self._dda_shader["camera_data"] = x, y, projection.near
        self._dda_shader["inv_view"] = ~self._projector.generate_view_matrix()
        self._density_gradient.use(0)

        old_func = self._win.ctx.blend_func
        self._win.ctx.blend_func = self._win.ctx.BLEND_ADDITIVE

        self._point_buffer.bind_to_storage_buffer()
        self._dda_geometry.render(self._dda_shader)

        self._win.ctx.blend_func = old_func

    def __getattr__(self, item):
        if item in self.__dict__["_dda_shader"]._uniforms:
            return self._dda_shader[item]
        return super().__getattribute__(item)

    def __setattr__(self, key, value):
        if (
            "_dda_shader" in self.__dict__
            and key in self.__dict__["_dda_shader"]._uniforms
        ):
            self._dda_shader[key] = value
        super().__setattr__(key, value)


class VoxelRenderer:

    def __init__(self):
        self._win = get_window()
        self._ctx = ctx = self._win.ctx

        self._point_buffer: gl.Buffer = None

        self._dda_shader = ctx.program(
            vertex_shader=read_text(shaders, "fullscreen_dda3d_vs.glsl"),
            fragment_shader=read_text(shaders, "fullscreen_dda3d_fs.glsl"),
        )

        self._dda_geometry = ctx.geometry(
            content=[
                gl.BufferDescription(
                    buffer=ctx.buffer(
                        data=array("f", (-1.0, -1.0, -1.0, 1.0, 1.0, -1.0, 1.0, 1.0))
                    ),
                    formats="2f",
                    attributes=["in_pos"],
                )
            ],
            mode=ctx.TRIANGLE_STRIP,
        )
        self.render_data: RenderData = None

    def validate_data(self):
        if not COLOUR_STEP.has_processed or COLOUR_STEP.data is self.render_data:
            return

        self.render_data = data = COLOUR_STEP.data
        self._dda_shader["density_scalar"] = data.density_scalar
        self._dda_shader["emission_brightness"] = data.emission_brightness

        orientation_shape = ORIENTATION_MAP[self.render_data.orientation]

        x_size, y_size, z_size = tuple(
            zip(*sorted(zip(orientation_shape, data.voxel_dimensions)))
        )[-1]
        x_count, y_count, z_count = tuple(
            zip(*sorted(zip(orientation_shape, data.voxel_counts)))
        )[-1]

        transposed = np.transpose(self.render_data.voxel_data, orientation_shape)
        magnitude = np.abs(transposed)
        linear_data = np.reshape(magnitude, -1)
        linear_data = linear_data / np.max(linear_data)

        data_count = len(linear_data)

        _buffer_size = _BUFFER_HEADER_SIZE + data_count * 0b0100
        if self._point_buffer is None:
            self._point_buffer = self._ctx.buffer(reserve=_buffer_size)
        elif self._point_buffer.size != _buffer_size:
            self._point_buffer.orphan(_buffer_size)

        byte_data = pack(
            f"i i i f f f {data_count}f",
            x_count,
            y_count,
            z_count,
            x_size,
            y_size,
            z_size,
            *linear_data,
        )
        self._point_buffer.write(byte_data)

    def draw(self):
        self.validate_data()
        if self.render_data is None:
            return

        old_func = self._ctx.blend_func
        self._win.ctx.blend_func = self._ctx.BLEND_ADDITIVE

        self.render_data.colour_map.use()
        self._point_buffer.bind_to_storage_buffer()
        self._dda_geometry.render(self._dda_shader)

        self._win.ctx.blend_func = old_func
