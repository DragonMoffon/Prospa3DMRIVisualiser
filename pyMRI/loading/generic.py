from typing import Self, NamedTuple
from pathlib import Path

import logging
log = logging.getLogger(Path(__file__).name)


try: # Try to use native filepickers via plyer
    import plyer
    def askopenfilename(title, filetypes, initialdir) -> str:
        """Plyer-based native file dialog binding.

        On Linux, this has additional config options which are documented in the source,
        but not on readthedocs at the moment. See the following for more:
        https://github.com/kivy/plyer/blob/2.1.0/plyer/platforms/linux/filechooser.py
        """
        try:
            data = plyer.filechooser.open_file(title=title, filetypes=filetypes, initialdir=initialdir)
            log.debug(data)
            return [data][0][0]
        except Exception as e:
            log.warning(f"Failed to pick file: {e}")
            return None

except ImportError as e:
    log.warning("Failed to import file_chooser from plyer, falling back to tkinter")
    from tkinter import filedialog
    askopenfilename = filedialog.askopenfilename


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
        path_str = askopenfilename(
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
