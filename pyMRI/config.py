from typing import NamedTuple


class MRIConfig(NamedTuple):
    path: str
    screen_width: int = 1280
    screen_height: int = 720
    acqu_name: str = "acqu.par"
    data_name: str = "data.3d"


def configure(*args):
    return MRIConfig(args[0])
