"""
LOADING THE DATA FROM A GIVEN FOLDER LOCATION (acqu.par [text], data.3d [little endian bytes])
"""
from typing import NamedTuple
from struct import unpack

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


def load_scan(mri_config: MRIConfig, scan_config: ScanConfig):
    file_path = f"{mri_config.path}\\{mri_config.data_name}"

    with open(file_path, "rb") as data_file:
        header = unpack(_HEADER_FORMAT, data_file.read(_HEADER_SIZE))
        print(header[0][::-1], header[1][::-1], header[2][::-1], header[3:])
        for line in iter(lambda: data_file.read(_LINE_SIZE), b''):
            if not line:
                break

            data = unpack('<f f f f', line)
            print(data)
