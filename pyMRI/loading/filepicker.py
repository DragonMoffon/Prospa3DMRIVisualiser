import sys
import logging

from pathlib import Path
from itertools import chain
from typing import Self, Sequence, NamedTuple

 
log = logging.getLogger(Path(__file__).name)
logging.basicConfig(level=logging.INFO)


def apply_platform_dir_suffix(path: Path | str) -> str:
    """Apply platform-specific trailing slashes for directories.

    Args:
        path: A `pathlib.Path` path or a string.
    Returns:
        A `str` version of the path which is resolved
        with a platform-appropriate trailing slash added
        if it's a directory.
    """
    pathlib_path = Path(path).resolve()
    use_path = str(pathlib_path)
    if pathlib_path.is_file():
        return use_path

    suffix = "\\" if sys.platform == "win32" else "/"
    if not use_path.endswith(suffix):
        use_path += suffix

    return use_path


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
        if initialdir is None:
            initialdir = Path.cwd()
        elif isinstance(initialdir, (Path, str)):
            initialdir = Path(initialdir).resolve()
        else:
            raise TypeError(
                f"initialdir must be a Path, str, or None, but got {initialdir}")

        # Account for the following edge cases:
        # 1. File paths are valid and act as "default" selections
        # 2. Windows (maybe) allows deleting a current directory
        if not initialdir.exists():
            raise ValueError(f"initialdir {inititaldir} does not exist")

        # Force filepickers to open in initialdir via trailing slashes
        use_path: str = apply_platform_dir_suffix(initialdir)
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

            # Match tkinter's API 1:1 by returning empty str on cancel
            chosen_file = ''
            if not data:
                log.info("Cancelled file selection")
            else:
                chosen_file = data[0]
                log.info(f"Picked file name: {chosen_file!r}")

            return chosen_file

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


__all__ = (
    'askopenfilename'
)

