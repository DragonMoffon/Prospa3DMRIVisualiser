import argparse
from typing import NamedTuple

from enum import Enum


class LaunchConfig(NamedTuple):
    screen_width: int = 1280
    screen_height: int = 720
    window_name: str = "Prospa 3D MRI visualiser"
    fullscreen: bool = False


def configure(*args) -> LaunchConfig:
    parser = argparse.ArgumentParser(
        prog="Prospa 3D MRI visualiser",
        description="visualise a 3D density cloud of an MRI scan"

    )
    parser.add_argument('--w', '--width', dest='screen_width', action='store', type=int, default=1280)
    parser.add_argument('--h', '--height', dest='screen_height', action='store', type=int, default=720)
    parser.add_argument('--window', '--window-name', '--name', dest='window', action='store', type=str, default='Prospa 3D MRI visualiser')
    parser.add_argument('--f', '--fs', '--fullscreen', dest='fullscreen', action='store_true', default=False)

    parsed_args = parser.parse_args(args)
    return LaunchConfig(
        parsed_args.screen_width,
        parsed_args.screen_height,
        parsed_args.window,
        parsed_args.fullscreen
    )
