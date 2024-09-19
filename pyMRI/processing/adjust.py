from pyMRI.processing.step import Step

from pyMRI.processing.data import (
    Unit,
    Orientation,
    ORIENTATIONS,
    UNIT_CONVERSIONS,
    FourierData,
)


class ConvertStep(Step[FourierData, FourierData]):

    def __init__(self, next: Step):
        super().__init__(next)
        self.new_unit: Unit = None
        self._ready = True

    def _recalculate(self, _input: FourierData) -> FourierData | None:
        if self.new_unit is None or self.new_unit == _input.voxel_unit:
            return _input
        c = UNIT_CONVERSIONS[_input.voxel_unit, self.new_unit]
        x, y, z = _input.voxel_dimensions
        nx, ny, nz = c * x, c * y, c * z
        if nx == 0.0 or ny == 0.0 or nz == 0.0:
            print(
                f"WARNING, UNSAFE TO CONVERT FROM {Unit.to_str(_input.voxel_unit)} TO {Unit.to_str(self.new_unit)}"
            )
            return _input

        dimensions = (nx, ny, nz)
        unit = self.new_unit
        return FourierData(
            _input.orientation, dimensions, unit, _input.voxel_counts, _input.voxel_data
        )


class ReorientStep(Step[FourierData, FourierData]):

    def __init__(self, next: Step):
        super().__init__(next)
        self.new_orientation: Orientation = None
        self._ready = True

    def _recalculate(self, _input: FourierData) -> FourierData:
        if self.new_orientation is None or self.new_orientation == _input.orientation:
            return _input

        return FourierData(
            self.new_orientation,
            _input.voxel_dimensions,
            _input.voxel_unit,
            _input.voxel_counts,
            _input.voxel_data,
        )


class InterpolateStep(Step[FourierData, FourierData]):

    def __init__(self, next: Step):
        super().__init__(next)

    def _recalculate(self, _input: FourierData) -> FourierData:
        return _input
