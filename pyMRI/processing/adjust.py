from scipy.interpolate import RegularGridInterpolator
from math import floor
import numpy as np

from pyMRI.processing.step import Step

from pyMRI.processing.data import (
    Unit,
    Orientation,
    ORIENTATIONS,
    UNIT_CONVERSIONS,
    InterpolateModes,
    FourierData,
)

# TODO: crop


class ConvertStep(Step[FourierData, FourierData]):

    def __init__(self, next: Step):
        super().__init__(next)
        with self.unready():
            self.new_unit: Unit = None

    def _reset(self) -> None:
        self.new_unit = None

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
        with self.unready():
            self.new_orientation: Orientation = None

    def _reset(self) -> None:
        self.new_orientation = None

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
        with self.unready():
            self.cubify: bool = False
            self.mode: InterpolateModes = InterpolateModes.NONE

    def _reset(self) -> None:
        self.cubify = False
        self.mode = InterpolateModes.NONE

    def _recalculate(self, _input: FourierData) -> FourierData:
        if self.mode is None or self.mode == InterpolateModes.NONE:
            return _input

        x_dim, y_dim, z_dim = _input.voxel_dimensions
        x_count, y_count, z_count = _input.voxel_counts

        x_size = x_dim / x_count
        y_size = y_dim / y_count
        z_size = z_dim / z_count

        x_space = np.linspace(0, x_dim, x_count)
        y_space = np.linspace(0, y_dim, y_count)
        z_space = np.linspace(0, z_dim, z_count)

        interp = RegularGridInterpolator(
            (x_space, y_space, z_space), _input.voxel_data, "linear"
        )

        match self.mode:
            case InterpolateModes.CUBE:
                # I don't think this is safe at all
                cube_size = min(x_size, y_size, z_size)

                nx_count = x_dim / cube_size
                ny_count = y_dim / cube_size
                nz_count = z_dim / cube_size

                if (
                    nx_count % 1.0 != 0.0
                    or ny_count % 1.0 != 0.0
                    or nz_count % 1.0 != 0.0
                ):
                    print("Cannot Easily Cubify, TODO a better method")
                    return _input

                nx_count = 1 if x_count == 1 else int(nx_count)
                ny_count = 1 if y_count == 1 else int(ny_count)
                nz_count = 1 if z_count == 1 else int(nz_count)
            case InterpolateModes.DOUBLE:
                nx_count = 2 * x_count if x_count != 1 else 1
                ny_count = 2 * y_count if y_count != 1 else 1
                nz_count = 2 * z_count if z_count != 1 else 1
            case InterpolateModes.TRIPLE:
                nx_count = 3 * x_count if x_count != 1 else 1
                ny_count = 3 * y_count if y_count != 1 else 1
                nz_count = 3 * z_count if z_count != 1 else 1
            case InterpolateModes.QUADRUPLE:
                nx_count = 4 * x_count if x_count != 1 else 1
                ny_count = 4 * y_count if y_count != 1 else 1
                nz_count = 4 * z_count if z_count != 1 else 1
            case InterpolateModes.MINIMUM:
                # Does this make sense?????
                # fmt: off
                nx_count = 1 if x_count == 1 else int(x_dim * 1000 if x_dim <= 1.0 else x_dim)
                ny_count = 1 if y_count == 1 else int(y_dim * 1000 if y_dim <= 1.0 else y_dim)
                nz_count = 1 if z_count == 1 else int(z_dim * 1000 if z_dim <= 1.0 else z_dim)
                # fmt: on
            case _:
                nx_count, ny_count, nz_count = _input.voxel_counts

        if nx_count == 0 or ny_count == 0 or nz_count == 0:
            print("INTERPOLATION MODE KILLS A DIMENSION")
            return _input
        # fmt: off
        """
        print(
            f'{x_dim} -> x: {x_count}, {x_dim/x_count}, nx: {nx_count}, {x_dim/nx_count} \n'
            f'{y_dim} -> y: {y_count}, {y_dim/y_count}, ny: {ny_count}, {y_dim/ny_count} \n'
            f'{z_dim} -> z: {z_count}, {z_dim/z_count}, nz: {nz_count}, {z_dim/nz_count}'
        )
        """
        # fmt: on

        nx_space = np.linspace(0, x_dim, nx_count)
        ny_space = np.linspace(0, y_dim, ny_count)
        nz_space = np.linspace(0, z_dim, nz_count)
        ix, iy, iz = np.meshgrid(
            nx_space, ny_space, nz_space, sparse=True, indexing="ij"
        )
        interpolated_data = interp((ix, iy, iz))
        return FourierData(
            _input.orientation,
            _input.voxel_dimensions,
            _input.voxel_unit,
            (nx_count, ny_count, nz_count),
            interpolated_data,
        )
