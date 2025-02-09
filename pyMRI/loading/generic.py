import sys
import logging

from pathlib import Path
from itertools import chain
from typing import Self, Sequence, NamedTuple


log = logging.getLogger(Path(__file__).name)
logging.basicConfig(level=logging.INFO)


# Use plyer's platform-native bindings if installed via pyMRI[extras]
try:
    import plyer
    log.info("Using plyer for platform-native filepicker")

    def askopenfilename(
        title: str ="Select a file",
        filetypes: list[tuple[str, str]] = (("All files", "*.*"),),
        initialdir: Path | str | None = None
    ) -> str | None:
        """Fetch a single filename using a platform-native dialog.

        This function aims to duplicate any features we need from
        `tkinter.filedialog.askopenfilename` with 1:1 fidelity:

        * accepts the same arguments and treating them the same way
        * returns `''` when a user cancels selection

        Args:
            title:
                Request the filepicker show a title if able.

            filetypes:
                A list of tuples consisting of:

                1. A display name
                2. One or more space-separated wildcard expressions.

            initialdir:
                A directory to open the as the initial view.

        Returns:
            A `str` containing a chosen path, or `None` if
            selectiong failed for any non-exception reason.
        """
        if isinstance(initialdir, (Path, str)):
            initialdir = Path(initialdir).resolve()
            # File paths are okay and act as "default" selections
            if not initialdir.exists():
                raise ValueError("Path does not exist")
        elif initialdir is not None:
            raise TypeError(
                f"initialdir must be a Path, str, or None, but got {initialdir}")

        # Force filepickers to open in initialdir via trailing slashes
        use_path: str | None = None
        if initialdir:
            use_path = str(initialdir)
            match (sys.platform, initialdir.is_dir()):
                case "win32", True:
                    suffix = "\\"
                case _,  True:
                    suffix = "/"
                case _, False:
                    suffix = ""
            if suffix and not use_path.endswith(suffix):
                use_path += suffix

        try:
            data = plyer.filechooser.open_file(
                title=title,
                # Despite plyer's doccstrings, space-separated *.ext
                # seems correct on tkinter and  all major platforms,
                # includin the most popular Linux file picker options.
                filters=filetypes,
                multiple=False,
                path=use_path
            )

            if data is None:
                log.info("Cancelled file selection")
            elif (filenames := data[0]):
                log.info(f"Picked file names: {', '.join((map(str, filenames)))}")
                return filenames[0]

            # Match tkinter's API 1:1 by returning empty str on cancel
            return ''

        except Exception as e:
            log.warning(f"Failed to pick file: {e}")
            return None


# The plyer platffrom bindings couldn't load found, so we'll use tkinter
except ImportError as e:
    log.info("Using tkinter file picker")
    from tkinter import filedialog, Tk
    # Reportedly, creating + hiding a root window helps askopenfilename behave
    # tk_root = Tk()
    # tk_root.wm_withdraw()
    askopenfilename = filedialog.askopenfilename


class FileLoader[T: NamedTuple]:
    dialog_title: str = "Select a file"
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
