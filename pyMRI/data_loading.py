"""
LOADING THE DATA FROM A GIVEN FOLDER LOCATION (acqu.par [text], data.3d [little endian bytes])
"""
from typing import NamedTuple
from struct import unpack

import numpy as np


class MRIConfig(NamedTuple):
    orient: str
    phase_2_FOV: int
    phase_1_FOV: int
    read_FOV: int
    phase_2_count: int
    phase_1_count: int
    read_count: int


def get_scan_config(acqu_path: str) -> MRIConfig:
    with open(acqu_path, "r") as acqu_file:
        lines = acqu_file.readlines()
        args = {line.split(" = ")[0]: line.split("=")[1].strip().strip("\"") for line in lines}

    default_cell_size = int(args['FOVr']) / int(args['Nread'])

    phase_1_fov = int(args['FOVp1']) if int(args['FOVp1']) else int(args['Nphase1']) * default_cell_size
    phase_2_fov = int(args['FOVp2']) if int(args['FOVp2']) else int(args['Nphase2']) * default_cell_size

    return MRIConfig(
        args['orient'],
        phase_2_fov,
        phase_1_fov,
        int(args['FOVr']),
        int(args['Nphase2']),
        int(args['Nphase1']),
        int(args['Nread']),
    )


_HEADER_SIZE = 0x00020
_HEADER_FORMAT = '<4s 4s 4s i i i i i'
_LINE_SIZE = 0x00010
_COMPLEX_SIZE = 0x00008


def load_scan(config: MRIConfig, data_path: str) -> np.ndarray[..., np.dtype[np.complexfloating]]:
    image_count = config.phase_2_count
    image_size = config.phase_1_count, config.read_count
    image_chunk_size = _COMPLEX_SIZE * image_size[0] * image_size[1]
    image_chunk_format = '<'+'f'*2*image_size[0]*image_size[1]

    image_array = np.zeros((image_count, image_size[0], image_size[1]), dtype=np.complexfloating)

    with open(data_path, "rb") as data_file:
        header = unpack(_HEADER_FORMAT, data_file.read(_HEADER_SIZE))
        print(header)
        for img_idx in range(image_count):
            data = unpack(image_chunk_format, data_file.read(image_chunk_size))
            image = np.zeros(image_size, dtype=np.complexfloating)
            for idx in range(0, 2*image_size[0]*image_size[1], 2):
                x = (idx // 2) % image_size[0]
                y = (idx // 2) // image_size[0]
                image[x, y] = data[idx] + 1j * data[idx+1]
            image_array[img_idx] = image

    return image_array

"""
def interpolate_scan(mri_config: MRIConfig, scan_config: ScanConfig, data: np.ndarray[..., np.dtype[np.complexfloating]]) -> tuple[ScanConfig, np.ndarray[..., np.dtype[np.complexfloating]]]:
    match mri_config.interpolate:
        case InterpolateMode.NONE:
            return scan_config, data
        case InterpolateMode.EVEN:
            raise NotImplementedError()
        case InterpolateMode.CM:
            raise NotImplementedError()
        case InterpolateMode.MM:
            raise NotImplementedError()
        case InterpolateMode.DOUBLE:
            interpolate_grid = RegularGridInterpolator((np.arange(scan_config.phase_2_count), np.arange(scan_config.phase_1_count), np.arange(scan_config.read_count)), data)
            n_p2 = scan_config.phase_2_count * 2
            n_p1 = scan_config.phase_1_count * 2
            n_r = scan_config.read_count * 2
            new_data = np.zeros((n_p2, n_p1, n_r), dtype=np.float64)

            for x in range(n_p2):
                dx = x * 0.5
                for y in range(n_p1):
                    dy = y * 0.5
                    for z in range(n_r):
                        dz = z * 0.5
                        print(dx, dy, dz)
                        print(interpolate_grid.grid)
                        new_data[x, y, z] = interpolate_grid((dx, dy, dz))

            new_scan_cfg = ScanConfig(
                scan_config.orient,
                scan_config.phase_2_FOV,
                scan_config.phase_1_FOV,
                scan_config.read_FOV,
                scan_config.phase_2_count*2,
                scan_config.phase_1_count*2,
                scan_config.read_count*2
            )

            print(data.shape)
            print(new_data.shape)
            return new_scan_cfg, new_data
        case InterpolateMode.TRIPLE:
            raise NotImplementedError()
        case InterpolateMode.QUADRUPLE:
            raise NotImplementedError()

    return scan_config, data
"""
