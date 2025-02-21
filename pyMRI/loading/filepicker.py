import sys
import logging

from pathlib import Path
from itertools import chain
from typing import Self, Sequence, NamedTuple

 
log = logging.getLogger(Path(__file__).name)
logging.basicConfig(level=logging.INFO)


def get_resolved_path(path: Path | str | None = None) -> Path:
    """Get an absolute value for `path` or the working directory.

    When `path` is `None`, it will be set to the return value
    of `pathlib.Path.cwd()`.

    This function improves testability and code quality via:

    1. wrapping path resolution in a unit-testable function
    2. avoiding monkeypatches of `pathlib.Path` (breaks pytest and more)

    Args:
        path:
            A path as a `str` or `pathlib.Path`, or `None`
            to use the current working directory as fetched
            by `pathlib.Path.cwd()`

    Raises:
        `TypeError` when `path` isn't a `Path`, `str`,
        or `None`.

    Returns:
        A resolved absolute `pathlib.Path` object.
    """
    if path is None:
        raw = Path.cwd()
    elif isinstance(path, (Path, str)):
        raw = Path(path)
    else:
        raise TypeError(
            f"got {path=!r} instead of a Path, str, or None")

    return raw.expanduser().resolve()


def apply_platform_dir_suffix(path: Path | str) -> str:
    """Apply platform-specific trailing slashes for directories.

    A platform-appropriate trailing slash tells a filepicker to
    open a view inside the directory rather than selecting the
    folder's icon in its parent directory.

    Args:
        path: A `pathlib.Path` path or a string.
    Returns:
        A `str` version of `path` resolved per pathlib
        and, if it's a dir, with a platform-specific slash
        at the end.
    """
    pathlib_path = get_resolved_path(path)
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
        title: str = "Select a file",
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
        resolved: Path = get_resolved_path(initialdir)

        # Account for the following edge cases:
        # 1. File paths are valid and act as "default" selections
        # 2. Windows (maybe) allows deleting a current directory
        if not resolved.exists():
            raise ValueError(f"initialdir {initialdir!r} does not exist")

        # Force filepickers to open in initialdir via trailing slashes
        use_path: str = apply_platform_dir_suffix(resolved)
        chosen_file: str | None = None
        try:
            data = plyer.filechooser.open_file(
                title=title,
                # Despite plyer's docstrings, space-separated *.ext
                # seems correct on tkinter and all major platforms,
                # including the most popular Linux file picker options.
                filters=filetypes,
                multiple=False,
                path=use_path
            )

            # Match tkinter's API 1:1 by returning empty str on cancel
            if not data:
                chosen_file = ''
                log.info("Cancelled file selection")
            else:
                chosen_file = data[0]
                log.info(f"Picked file name: {chosen_file!r}")

        except Exception as e:
            log.warning(f"Failed to pick file: {e}")

        finally:
            return chosen_file


# The plyer platffrom bindings couldn't load found, so we'll use tkinter
except ImportError as e:
    log.info("Using tkinter file picker")
    from tkinter import filedialog, Tk
    # Reportedly, creating + hiding a root window helps askopenfilename behave
    # tk_root = Tk()
    # tk_root.wm_withdraw()
    askopenfilename = filedialog.askopenfilename


__all__ = (
    'apply_platform_dir_suffix',
    'askopenfilename',
    'get_resolved_path',
)

