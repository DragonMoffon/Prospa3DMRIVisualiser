import argparse
from typing import NamedTuple

from enum import Enum


class InterpolateMode(Enum):
    NONE = 0
    EVEN = 1
    MM = 2
    CM = 3
    DOUBLE = 4
    TRIPLE = 5
    QUADRUPLE = 6


class MRIConfig(NamedTuple):
    path: str
    screen_width: int = 1280
    screen_height: int = 720
    acqu_name: str = "acqu.par"
    data_name: str = "data.3d"
    interpolate: InterpolateMode = InterpolateMode.NONE


def configure(*args):
    parser = argparse.ArgumentParser(
        prog="Prospa 3D MRI visualiser",
        description="visualise a 3D density cloud of an MRI scan"

    )
    parser.add_argument('location', action='store', type=str)
    parser.add_argument('--w', '--width', dest='screen_width', action='store', type=int, default=1280)
    parser.add_argument('--h', '--height', dest='screen_height', action='store', type=int, default=720)
    parser.add_argument('--acqu', '--acqu_name', '--config', dest='acqu', action='store', type=str, default='acqu.par')
    parser.add_argument('--data', '--data_name', '--scan', dest='data', action='store', type=str, default='data.3d')
    parser.add_argument('--interpolate', '--interp', dest='interp', choices=['NONE', 'EVEN', 'MM', 'CM', 'DOUBLE', 'TRIPLE', 'QUADRUPLE'], action='store', type=str, default='NONE')

    parsed_args = parser.parse_args(args)
    return MRIConfig(
        parsed_args.location,
        parsed_args.screen_width,
        parsed_args.screen_height,
        parsed_args.acqu,
        parsed_args.data,
        InterpolateMode[parsed_args.interp]
    )
