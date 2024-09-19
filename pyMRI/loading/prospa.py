"""
File Loading of complex data from Prospa files.

works on .1d, .2d, .3d files
also requires a .par file

Can work without the parameter file but is a lossy option

Loading Path:

Pick .<x>d file
Choose .par file
if no <.par>
    Get Voxel Size
    Get Orientation
end
generate data
"""

from typing import NamedTuple
from struct import unpack

from numpy import ndarray, complexfloating, zeros, shape

from pyMRI.loading.generic import FileLoader

_HEADER_SIZE = 0x00020
_HEADER_FORMAT = "<4s 4s 4s i i i i i"
_LINE_SIZE = 0x00010
_COMPLEX_SIZE = 0x00008


class ProspaData(NamedTuple):
    count: tuple[int, int, int]
    data: ndarray[complexfloating]


class ProspaDataLoader(FileLoader[ProspaData]):
    dialog_title: str = "Select a Prospa Data File"
    accepted_file_types: list[tuple[str, str]] = [
        ("Prospa Density Data", "*.*d"),
        ("Prospa Density Data 3D", "*.3d"),
        ("Prospa Density Data 2D", "*.2d"),
        ("Prospa Density Data 1D", "*.1d"),
    ]

    def load(self) -> ProspaData:
        with open(self.path, "rb") as data_file:
            _, _, _, _, img_width, img_height, img_count, _ = unpack(
                _HEADER_FORMAT, data_file.read(_HEADER_SIZE)
            )
            image_chunk_size = _COMPLEX_SIZE * img_width * img_height
            image_chunk_format = "<" + "f" * (2 * img_width * img_height)
            images = zeros([img_count, img_width, img_height], dtype=complexfloating)

            for img in images[:]:
                data = unpack(image_chunk_format, data_file.read(image_chunk_size))
                for idx in range(img_width * img_height):
                    value = data[2 * idx] + 1j * data[2 * idx + 1]
                    img[idx % img_width, idx // img_width] = value

            self._data = ProspaData((img_count, img_width, img_height), images)
            return self._data


class ProspaParameters(NamedTuple):
    orient: str
    phase_2: int
    phase_1: int
    read: int
    img_count: int
    img_width: int
    img_height: int
    # TODO fill with other prospa parameters


class ProspaParametersLoader(FileLoader[ProspaParameters]):
    dialog_title: str = "Select a Prospa parameter File"
    accepted_file_types: list[tuple[str, str]] = [("Prospa Parameters", "*.par")]

    def load(self) -> ProspaParameters:
        with open(self.path, "r") as par_file:
            lines = par_file.readlines()
            args = {
                line.split(" = ")[0]: line.split("=")[1].strip().strip('"')
                for line in lines
            }

        default_cell_size = int(args["FOVr"]) / int(args["Nread"])

        phase_1_fov = (
            int(args["FOVp1"])
            if int(args["FOVp1"])
            else int(args["Nphase1"]) * default_cell_size
        )
        phase_2_fov = (
            int(args["FOVp2"])
            if int(args["FOVp2"])
            else int(args["Nphase2"]) * default_cell_size
        )

        self._data = ProspaParameters(
            args["orient"].lower(),
            phase_2_fov,
            phase_1_fov,
            int(args["FOVr"]),
            int(args["Nphase2"]),
            int(args["Nphase1"]),
            int(args["Nread"]),
        )
        return self._data
