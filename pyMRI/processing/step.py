from __future__ import annotations
from typing import NamedTuple, Self


class Step[O: NamedTuple]:

    def __init__(self, next_step: Step):
        self._next: Step = next_step
        self._input: NamedTuple = None
        self._output: O = None

    @property
    def data(self) -> O:
        if self._data is None:
            raise ValueError("Step {self} has not yet been processed")

        return self._data

    def update(self, _input: NamedTuple) -> O:
        _output = self._recalculate(previous)
        self._input = _input
        self._output = _output
        self.next_step.update(_output)

    def _recalculate(self, previous: I) -> O:
        raise NotImplementedError

    def serialise(self) -> dict:
        raise NotImplementedError

    @classmethod
    def deserialise(self, config: dict) -> Self:
        raise NotImplementedError
