"""
LOADING THE DATA FROM A GIVEN FOLDER LOCATION (acqu.par [text], data.3d [little endian bytes])
"""
from typing import NamedTuple

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


def load_scan(mri_config: MRIConfig, scan_config: ScanConfig):
    pass
