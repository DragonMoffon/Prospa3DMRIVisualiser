from typing import NamedTuple

from numpy import ndarray, complexfloating

class FileData(NamedTuple):
    orientation: str
    voxel_dimensions: tuple[int, int, int]
    voxel_counts: tuple[int, int, int]
    voxel_data: ndarray[complexfloating]