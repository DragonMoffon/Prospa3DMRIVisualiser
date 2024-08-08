# TODO: File Loader
# Data Processing

from typing import Self, NamedTuple
from pathlib import Path

from tkinter import filedialog

class FileLoader[T: NamedTuple]:
    dialog_title: str = 'select a file'
    accepted_file_types: list[tuple[str, str]] = [('All Files', '*.*')]

    
    def __init__(self, path: str | Path):
        self.path: str | Path = path
        self._data: T = None

    @property
    def data(self):
        if self._data is None:
            raise ValueError('FileLoader has not yet loaded it\'s specified file')
        return self._data

    @classmethod
    def fetch(cls) -> Self | None:
        path_str = filedialog.askopenfilename(title=cls.dialog_title, filetypes=cls.accepted_file_types)
        print(path_str)
        if not path_str:
            return
        return cls(Path(path_str))

    def load(self) -> T:
        raise NotImplementedError

        
Files = dict[str, FileLoader]
