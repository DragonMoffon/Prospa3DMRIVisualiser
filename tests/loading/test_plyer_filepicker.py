import sys
import logging

from pathlib import Path
from typing import Final
from unittest.mock import Mock, MagicMock
import pytest
import plyer

from pyMRI.loading.filepicker import askopenfilename, apply_platform_dir_suffix


WIN32: Final[str] = "win32"
LINUX: Final[str] = "linux"
MAC: Final[str] = "darwin"
PLATFORMS: Final[tuple[str]] = (WIN32, LINUX, MAC)


def make_mock_path(
    str_value: str,
    is_file: bool = False,
    is_dir: bool = False,
    exists: bool | None = None
):
    """Fake a pathlib.Path via unittest.mock's MagicMock and Mock classes.
    
    The exists argument auto-configures itself from is_file and is_dir
    unless you provide a specific bool value. This allows handling an
    edge case in file loading where the target path has been deleted
    before we can access the data.

    Args:
        str_value:
            What __str__ should return, i.e. str(path).
        is_file:
            What path.is_file() should return.
        is_dir:
            What path.is_dir() should return.
        exists:
            Set this to False to handle a very specific edge case in
            file loading: the file or dir was deleted before we can
            access it.
    Returns:
        A unittest.mock.MagicMock of a pathlib.Path configured to
        act as just enough Path 
    """
    # No validation b/c this isn't user-facing code, just tests
    if exists is None:
        exists = is_file or is_dir

    mock_path = MagicMock(Path)

    mock_path.__str__ = Mock(return_value=str_value)
    mock_path.is_file = Mock(return_value=is_file)
    mock_path.is_dir = Mock(return_value=is_dir)
    mock_path.exists = Mock(return_value=exists)

    return mock_path


@pytest.fixture(params=PLATFORMS)
def platform(
    request,  # Access the value from params passed
    monkeypatch  # pytest built-in fixture which auto-reverts changes
) -> str:
    """Make sys.platform return the value we'll be returning here"""
    monkeypatch.setattr(sys, "platform", request.param)
    return request.param


@pytest.fixture
def platform_slash(platform: str) -> str:
    """Backslash on Windows, forward on all other OSes."""
    return "\\" if platform == WIN32 else "/"


@pytest.fixture
def users_root(platform) -> str:
    """A pretend home parent directory where user home folders go."""
    return "C:\\Users" if platform == WIN32 else "/home"


@pytest.fixture
def user_home_dir(monkeypatch, users_root: str, platform_slash: str) -> str:
    """The mock user's home directory as a string."""
    value = platform_slash.join([users_root, "MockUser"])
    return value


@pytest.fixture
def raw_target_dir(
    user_home_dir: str,
    platform_slash: str,
    target_dir: str = "target_dir"
) -> str:
    """Imitate a platform-specific path for a folder in a user dir."""
    return platform_slash.join([user_home_dir, target_dir])


@pytest.fixture
def mock_dir_path(monkeypatch, raw_target_dir):
    mock_path = make_mock_path(raw_target_dir, is_dir=True)
    mock_resolve_func = Mock(return_value=mock_path)
    monkeypatch.setattr(
        "pyMRI.loading.filepicker.get_resolved_path", mock_resolve_func)

    return mock_path


@pytest.fixture
def raw_file_path(
    user_home_dir: str,
    platform_slash: str,
    target_file: str = "file.ext"
):
    """Fake file in the home dir."""
    return platform_slash.join([user_home_dir, target_file])


@pytest.fixture
def mock_file_path(monkeypatch, raw_file_path):
    mock_path = make_mock_path(raw_file_path, is_file=True)
    mock_resolve = Mock(return_value=mock_path)
    monkeypatch.setattr(
        "pyMRI.loading.filepicker.get_resolved_path", mock_resolve)

    return mock_path


def test_apply_platform_dir_suffix_does_nothing_to_file_paths(mock_file_path):
    """When Path.is_file() returns True, no suffix is added."""
    assert apply_platform_dir_suffix(mock_file_path) == str(mock_file_path)


def test_apply_platform_dir_suffix_appends_platform_slash(
    monkeypatch,
    platform_slash,
    mock_dir_path
):
    """When a Path.is_dir() returns True, a platform-appropriate suffix is added."""
    assert apply_platform_dir_suffix(mock_dir_path).endswith(platform_slash)


@pytest.mark.parametrize(
    "value_with_wrong_type",
    (1, 2.2, ('tuples', 'are', 'not', 'ok', 'here'))
)
def test_plyer_askopenfilename_raises_typeerror_on_wrong_type_for_initialdir(
    value_with_wrong_type
):
    with pytest.raises(TypeError):
        _ = askopenfilename(initialdir=value_with_wrong_type)


def test_askcancelled_file_selection_returns_empty_string(
    monkeypatch,
    mock_dir_path
):
    # Fail to return any data at all
    mock_open_file_func = Mock(return_value=None)
    monkeypatch.setattr("plyer.filechooser.open_file", mock_open_file_func)

    assert askopenfilename(initialdir=mock_dir_path) == ''


@pytest.mark.parametrize("exception_type", (TypeError, ValueError, RuntimeError))
def test_plyer_askopenfilename_logs_opentime_logs_exceptions_and_returns_none(
    monkeypatch,
    mock_dir_path,
    exception_type
):
    # Unique to this test
    mock_log = Mock()
    mock_open_file_func = Mock(side_effect=exception_type("bad"))
    monkeypatch.setattr(
        "pyMRI.loading.filepicker.log", mock_log)
    monkeypatch.setattr(
        "plyer.filechooser.open_file", mock_open_file_func)

    # Perform the "failing" call and store the result
    result = askopenfilename(initialdir=mock_dir_path)

    # Did we log the warning?
    mock_log.warning.assert_called_once()
    # Did we get a None return
    assert result is None

