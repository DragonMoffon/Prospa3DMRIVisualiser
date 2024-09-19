import numpy as np
from numpy import fft

from pyMRI.processing.step import Step
from pyMRI.processing.data import FileData, FourierData


# TODO
class ShiftStep(Step[FileData, FourierData]):

    def _recalculate(self, _input: FileData) -> FourierData:
        return _input


# TODO
class FilterStep(Step[FourierData, FourierData]):

    def _recalculate(self, _input: FourierData) -> FourierData:
        return _input


class FourierStep(Step[FileData, FourierData]):
    def __init__(self, next: Step):
        super().__init__(next)
        self.should_transform_data: bool = False
        self._ready = True

    def _recalculate(self, _input: FileData) -> FourierData | None:
        if not self.should_transform_data:
            return _input
        transformed_data = fft.ifftn(_input.voxel_data)

        return FourierData(
            _input.orientation,
            _input.voxel_dimensions,
            _input.voxel_unit,
            _input.voxel_counts,
            transformed_data,
        )
