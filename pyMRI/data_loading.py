"""
LOADING THE DATA FROM A GIVEN FOLDER LOCATION (acqu.par [text], data.3d [little endian bytes])
"""
from typing import NamedTuple
from struct import unpack

import numpy as np

from pyMRI.config import MRIConfig


class ScanConfig(NamedTuple):
    orient: str
    phase_1_FOV: int
    phase_2_FOV: int
    read_FOV: int
    phase_1_count: int
    phase_2_count: int
    read_count: int


def get_scan_config(config: MRIConfig) -> ScanConfig:
    path = config.path
    acqu_name = config.acqu_name
    with open(f"{path}\\{acqu_name}", "r") as acqu_file:
        lines = acqu_file.readlines()
        args = {line.split(" = ")[0]: line.split("=")[1].strip().strip("\"") for line in lines}

    return ScanConfig(
        args['orient'],
        int(args['FOVp1']),
        int(args['FOVp2']),
        int(args['FOVr']),
        int(args['Nphase1']),
        int(args['Nphase2']),
        int(args['Nread'])
    )


_HEADER_SIZE = 0x00020
_HEADER_FORMAT = '<4s 4s 4s i i i i i'
_LINE_SIZE = 0x00010
_COMPLEX_SIZE = 0x00008


def load_scan(mri_config: MRIConfig, scan_config: ScanConfig) -> np.ndarray[..., np.dtype[np.complexfloating]]:
    file_path = f"{mri_config.path}\\{mri_config.data_name}"

    image_count = scan_config.phase_2_count
    image_size = scan_config.phase_1_count, scan_config.read_count
    image_chunk_size = _COMPLEX_SIZE * image_size[0] * image_size[1]
    image_chunk_format = '<'+'f'*2*image_size[0]*image_size[1]

    image_array = np.zeros((image_count, image_size[0], image_size[1]), dtype=np.complexfloating)

    with open(file_path, "rb") as data_file:
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


def transform_scan(mri_config: MRIConfig, scan_config: ScanConfig, k_space: np.ndarray[..., np.dtype[np.complexfloating]]) -> np.ndarray[..., np.dtype[np.complexfloating]]:
    pass
