from __future__ import annotations
from typing import NamedTuple, Self, Any


class Step[I: NamedTuple | None, O: NamedTuple]:

    def __init__(self, next_step: Step):
        self._ready: bool = False
        self._next: Step = next_step
        self._input: I = None
        self._output: O = None

    @property
    def has_processed(self) -> bool:
        return self._output is not None

    @property
    def data(self) -> O:
        if self._output is None:
            raise ValueError("Step {self} has not yet been processed")

        return self._output

    def update(self, _input: NamedTuple) -> O:
        _output = self._recalculate(_input)
        if _output is None:
            return
        self._input = _input
        self._output = _output
        if self._next is not None:
            self._next.update(_output)

    def _recalculate(self, previous: I) -> O | None:
        raise NotImplementedError

    def serialise(self) -> dict:
        raise NotImplementedError

    @classmethod
    def deserialise(self, config: dict) -> Self:
        raise NotImplementedError

    def __setattr__(self, name: str, value: Any):
        object.__setattr__(self, name, value)
        if not self._ready or name.startswith("_"):
            return
        self.update(self._input)
