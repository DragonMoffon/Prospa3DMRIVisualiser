from __future__ import annotations
from contextlib import contextmanager
from typing import NamedTuple, Self, Any


class Step[I: NamedTuple | None, O: NamedTuple]:

    def __init__(self, next_step: Step):
        self._ready: bool = True
        self._next: Step = next_step
        self._input: I = None
        self._output: O = None

    def _safe_set(self, attr: str, value: Any) -> None:
        object.__setattr__(self, attr, value)

    @contextmanager
    def unready(self):
        try:
            self._ready = False
            yield self
        finally:
            self._ready = True

    @property
    def has_processed(self) -> bool:
        return self._output is not None

    @property
    def data(self) -> O:
        if self._output is None:
            raise ValueError("Step {self} has not yet been processed")

        return self._output

    def reset(self) -> None:
        with self.unready():
            self._reset()
        if self._next is not None:
            self._next.reset()

    def _reset(self) -> None:
        self._input = None
        self._output = None

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
