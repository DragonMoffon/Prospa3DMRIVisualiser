import numpy as np

from arcade import get_window, ArcadeContext
from arcade.gl import Texture2D, CLAMP_TO_EDGE

from pyMRI.processing.step import Step
from pyMRI.processing.data import FourierData, RenderData

# -- TEMP --
from importlib.resources import files, as_file
import pyMRI.rendering.shaders as src
from PIL import Image

COLOUR_TEXTURE_WIDTH = 256


class ColourStep(Step[FourierData, RenderData]):

    def __init__(self, next):
        super().__init__(next)
        with self.unready():
            self._ctx: ArcadeContext = None
            self._colour_points = []  # TODO
            self._colour_texture: Texture2D = None
            self.density_scalar: float = 0.05
            self.emission_brightness: float = 1.0

    def _reset(self):
        self._colour_points = []
        self.density_scalar = 0.05
        self.emission_brightness = 1.0

    def _recalculate(self, _input: FourierData):
        if self._ctx is None:
            self._ctx = get_window().ctx

        if self._colour_texture is None:
            with as_file((files(src) / "turbo.png")) as path:
                img = Image.open(path).resize((COLOUR_TEXTURE_WIDTH, 1)).convert("RGBA")
            data = img.tobytes()
            self._colour_texture = self._ctx.texture(
                (COLOUR_TEXTURE_WIDTH, 1),
                wrap_x=CLAMP_TO_EDGE,
                wrap_y=CLAMP_TO_EDGE,
                data=data,  # 4 floats per colour
            )

        # TODO: figure out colour data from colour points

        return RenderData(
            self._colour_texture,
            self.density_scalar,
            self.emission_brightness,
            _input.orientation,
            _input.voxel_dimensions,
            _input.voxel_unit,
            _input.voxel_counts,
            _input.voxel_data,
        )


class CameraStep(Step):

    def _recalculate(self, _input):
        return _input
