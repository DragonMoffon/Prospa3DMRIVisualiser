"""
File Loading of complex data from Prospa files.

works on .1d, .2d, .3d files
can also use acqu.par files for more data

The prospa format:
little endian
Header:
    -> Source (little endian chars) {v1.1 Data Pros}
    -> unknown (32-bit int)
    -> Read Count (32-bit int) {'img width'}
    -> Phase 1 Count (32-bit int) {'img height'}
    -> Phase 2 Count (32-bit int) {'img count'}

From the parameter file.
the orientation defines how the axis where used
the last axis is the read count
the second to last axis is the phase 1 count
the first axis is the phase 2 count

this means that for 'XYZ', X is the phase 2, Y is the phase 1, and Z is the read axis.
"""

from typing import NamedTuple
from struct import unpack

from numpy import ndarray, complexfloating, zeros

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
            images = zeros([img_count, img_height, img_width], dtype=complexfloating)

            for img in images[:]:
                data = unpack(image_chunk_format, data_file.read(image_chunk_size))
                for idx in range(img_width * img_height):
                    value = data[2 * idx] + 1j * data[2 * idx + 1]
                    img[idx % img_height, idx // img_height] = value

            self._data = ProspaData((img_count, img_height, img_width), images)
            return self._data


class ProspaParameters(NamedTuple):
    orient: str
    phase_2: int
    phase_1: int
    read: int  # Last orientation element
    img_count: int
    img_height: int
    img_width: int  # Last orientation element
    # TODO fill with other prospa parameters


class ProspaParametersLoader(FileLoader[ProspaParameters]):
    dialog_title: str = "Select a Prospa parameter File"
    accepted_file_types: list[tuple[str, str]] = [("Prospa Parameters", "*.par")]

    def load(self) -> ProspaParameters:
        with open(self.path, "r") as par_file:
            lines = par_file.readlines()
            args = {
                line.split("=")[0].strip(): line.split("=")[1].strip().strip('"')
                for line in lines
            }

        default_cell_size = float(args["FOVr"]) / float(args["Nread"])

        phase_1_fov = (
            float(args["FOVp1"])
            if float(args["FOVp1"])
            else float(args["Nphase1"]) * default_cell_size
        )
        phase_2_fov = (
            float(args["FOVp2"])
            if float(args["FOVp2"])
            else float(args["Nphase2"]) * default_cell_size
        )

        self._data = ProspaParameters(
            args["orient"].lower(),
            phase_2_fov,
            phase_1_fov,
            float(args["FOVr"]),
            int(args["Nphase2"]),
            int(args["Nphase1"]),
            int(args["Nread"]),
        )
        return self._data
