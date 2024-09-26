import numpy as np
from numpy import fft

from pyMRI.processing.step import Step
from pyMRI.processing.data import FileData, FourierData, FourierMode, FourierNorm


# TODO
class ShiftStep(Step[FileData, FourierData]):

    def __init__(self, next: Step):
        super().__init__(next)
        with self.unready():
            self.shift_x: bool = False
            self.shift_y: bool = False
            self.shift_z: bool = False
            self.inverse: bool = False

    def _recalculate(self, _input: FileData) -> FourierData:
        if not (self.shift_x or self.shift_y or self.shift_z):
            return _input

        func = np.fft.ifftshift if self.inverse else np.fft.fftshift
        axes = (
            ((0,) if self.shift_x else ())
            + ((1,) if self.shift_y else ())
            + ((2,) if self.shift_z else ())
        )
        return FourierData(
            _input.orientation,
            _input.voxel_dimensions,
            _input.voxel_unit,
            _input.voxel_counts,
            func(_input.voxel_data, axes),
        )


# TODO
class FilterStep(Step[FourierData, FourierData]):

    def _recalculate(self, _input: FourierData) -> FourierData:
        return _input


class FourierStep(Step[FileData, FourierData]):
    def __init__(self, next: Step):
        super().__init__(next)
        with self.unready():
            self.should: bool = False
            self.inverse: bool = False
            self.mode: FourierMode = FourierMode.THREE
            self.norm: FourierNorm = FourierNorm.BACKWARD

    def _recalculate(self, _input: FileData) -> FourierData | None:
        if not self.should:
            return _input

        if len(_input.orientation) == 1:
            with self.unready():
                self.mode = FourierMode.ONE
        if len(_input.orientation) == 2 and self.mode == FourierMode.THREE:
            with self.unready():
                self.mode = FourierMode.TWO

        transformed_data = np.zeros(_input.voxel_data.shape, dtype=np.complexfloating)
        match self.mode:
            case FourierMode.ONE:
                axes = (-1,)
            case FourierMode.TWO:
                axes = (-2, -1)
            case FourierMode.THREE:
                axes = (-3, -2, -1)

        func = np.fft.ifftn if self.inverse else np.fft.fftn

        func(_input.voxel_data, None, axes, self.norm, transformed_data)

        return FourierData(
            _input.orientation,
            _input.voxel_dimensions,
            _input.voxel_unit,
            _input.voxel_counts,
            transformed_data,
        )
