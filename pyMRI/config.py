from typing import NamedTuple


class MRIConfig(NamedTuple):
    path: str
    screen_width: int = 1280
    screen_height: int = 720


def configure(*args):
    return MRIConfig(args[0])
