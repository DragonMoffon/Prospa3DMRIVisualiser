from pyMRI.processing.data import (
    FileData,
    FourierData,
    RenderData,
    Orientation,
    ORIENTATIONS,
    ORIENTATION_MAP,
    Unit,
    UNIT_CONVERSIONS,
    InterpolateModes,
    FourierMode,
    FourierNorm,
)

from pyMRI.processing.loading import FileLoaderStep
from pyMRI.processing.fourier import ShiftStep, FilterStep, FourierStep
from pyMRI.processing.adjust import ConvertStep, ReorientStep, InterpolateStep
from pyMRI.processing.style import ColourStep, CameraStep

__all__ = (
    "Orientation",
    "ORIENTATIONS",
    "ORIENTATION_MAP",
    "Unit",
    "UNIT_CONVERSIONS",
    "FileData",
    "FILE_LOADER_STEP",
    "FourierData",
    "PRE_SHIFT_STEP",
    "FILTER_STEP",
    "FourierMode",
    "FourierNorm",
    "FOURIER_STEP",
    "POST_SHIFT_STEP",
    "InterpolateModes",
    "CONVERT_STEP",
    "REORIENT_STEP",
    "INTERPOLATE_STEP",
    "RenderData",
    "COLOUR_STEP",
    "CAMERA_STEP",
)


"""
Steps:
* Load File
* Shift Data
* Filter Data
* Transorm Data
* Convert Data
* Reorient Data
* Interpolate Data
* Colour Data
* Orient Camera
* Mesh Data
* Save Data
"""

SAVE_STEP = None
MESH_STEP = None
CAMERA_STEP = CameraStep(MESH_STEP)
COLOUR_STEP = ColourStep(CAMERA_STEP)
INTERPOLATE_STEP = InterpolateStep(COLOUR_STEP)
REORIENT_STEP = ReorientStep(INTERPOLATE_STEP)
CONVERT_STEP = ConvertStep(REORIENT_STEP)
POST_SHIFT_STEP = ShiftStep(CONVERT_STEP)
FOURIER_STEP = FourierStep(POST_SHIFT_STEP)
FILTER_STEP = FilterStep(FOURIER_STEP)
PRE_SHIFT_STEP = ShiftStep(FILTER_STEP)
FILE_LOADER_STEP = FileLoaderStep(PRE_SHIFT_STEP)
