import numpy as np

from pyMRI.processing.step import Step
from pyMRI.processing.data import FileData, FourierData, FourierMode, FourierNorm

from PIL import Image


# TODO
class ShiftStep(Step[FileData, FourierData]):

    def __init__(self, next: Step):
        super().__init__(next)
        with self.unready():
            self.shifts: tuple[int, int, int] = (0, 0, 0)

    def _recalculate(self, _input: FileData) -> FourierData:
        if not any(self.shifts):
            return _input

        return _input.update(
            voxel_data=np.roll(_input.voxel_data, self.shifts, (0, 1, 2)),
        )


def _gaussian_kernal1d(sx, nsig):
    x = np.linspace(-0.5 * (sx - 1), 0.5 * (sx - 1), sx)
    gx = np.exp(-0.5 * np.square(x) / np.square(nsig))
    return gx


def _gaussian_kernal2d(shape, nsig):
    sx, sy = shape
    gx = _gaussian_kernal1d(sx, nsig)
    gy = _gaussian_kernal1d(sy, nsig)

    return np.einsum("i,j->jk", gx, gy)


def _gaussian_kernal3d(shape, nsig):
    sx, sy, sz = shape
    gx = _gaussian_kernal1d(sx, nsig)
    gy = _gaussian_kernal1d(sy, nsig)
    gz = _gaussian_kernal1d(sz, nsig)
    return np.einsum("i,j,k->ijk", gx, gy, gz)


# TODO
class FilterStep(Step[FourierData, FourierData]):

    def __init__(self, next: Step):
        super().__init__(next)
        with self.unready():
            self.low_pass: bool = True
            self.high_pass: bool = False
            self.band_pass: bool = False
            self.gaussian: bool = True
            self.low_pass_radius: float = 1.0
            self.high_pass_radius: float = 1.0
            self.band_pass_radius: float = 1.0
            self.band_pass_target: float = 1.0

    def _recalculate(self, _input: FourierData) -> FourierData:
        if not (self.low_pass or self.high_pass or self.band_pass):
            return _input

        filtered = _input.voxel_data

        if self.low_pass:
            low_kern = _gaussian_kernal3d(_input.voxel_data.shape, self.low_pass_radius)
            filtered = filtered * low_kern / np.sum(low_kern)

        if self.high_pass:
            high_kern = 1 - _gaussian_kernal3d(
                _input.voxel_data.shape, self.high_pass_radius
            )
            filtered = filtered * high_kern / np.sum(high_kern)

        if self.band_pass:
            # TODO
            pass

        return _input.update(voxel_data=filtered)


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
            np.abs(transformed_data),
        )
