from typing import Self, NamedTuple
from pathlib import Path

from tkinter import filedialog


class FileLoader[T: NamedTuple]:
    dialog_title: str = "select a file"
    accepted_file_types: list[tuple[str, str]] = [("All Files", "*.*")]

    def __init__(self, path: str | Path):
        self.path: str | Path = path
        self._data: T = None

    @property
    def data(self) -> T:
        if self.path is None:
            raise ValueError("FileLoader has no path set")
        if self._data is None:
            self._data = self.load()
        return self._data

    @property
    def is_loaded(self) -> bool:
        return self._data is not None

    @classmethod
    def fetch(cls, start_folder: Path = None) -> Self | None:
        path_str = filedialog.askopenfilename(
            title=cls.dialog_title,
            filetypes=cls.accepted_file_types,
            initialdir=start_folder,
        )
        if not path_str:
            return
        return cls(Path(path_str))

    def load(self) -> T:
        raise NotImplementedError


Files = dict[str, FileLoader]
