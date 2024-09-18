from enum import Enum

from pyMRI.processing.step import Step


class InterpolateMode(Enum):
    NONE = 0
    EVEN = 1
    MM = 2
    CM = 3
    DOUBLE = 4
    TRIPLE = 5
    QUADRUPLE = 6


class OrientStep(Step):

    def __init__(self, next_step: Step):
        super().__init__(next_step)
        self.new_orientation: str = None


class ShiftStep(Step):

    def __init__(self, next: Step):
        super().__init__(next)
        self.x_shift: int = 0
        self.y_shift: int = 0
        self.z_shift: int = 0


class InterpolateStep(Step):

    def __init__(self, next: Step):
        super().__init__(next)
        self.mode: InterpolateMode = InterpolateMode.NONE