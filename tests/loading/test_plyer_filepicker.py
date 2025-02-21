import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock
import pytest

from pyMRI.loading.filepicker import askopenfilename, apply_platform_dir_suffix


WIN32 = "win32"
LINUX = "linux"
MAC = "darwin"
PLATFORMS = (WIN32, LINUX, MAC)


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

    path = MagicMock(Path)

    path.__str__ = Mock(return_value=str_value)
    path.is_file = Mock(return_value = is_file)
    path.is_dir = Mock(return_value = is_dir)
    path.exists = Mock(return_value = exists)
    
    return path


@pytest.fixture(params=PLATFORMS)
def platform(
    request,  # Access the value from params passed
    monkeypatch  # pytest built-in fixture which auto-reverts changes
):
    monkeypatch.setattr(sys, "platform", request.param)
    return request.param


@pytest.fixture
def platform_slash(platform):
    return "\\" if platform == WIN32 else "/"


@pytest.fixture
def users_root(platform):
    return "C:\\Users" if platform == WIN32 else "/home"


@pytest.fixture
def raw_target_dir(users_root, platform_slash) -> str:
    """Imitate a platform-specific path for a folder in a user dir."""
    return platform_slash.join([users_root, "user", "target_dir"])


def test_apply_platform_dir_suffix_does_nothing_to_file_paths(
    monkeypatch, platform
):
    """When Path.is_file() returns True, no suffix is added."""

    path = make_mock_path("file.ext", is_file=True)
    monkeypatch.setattr(Path, "resolve", lambda self: path)

    assert apply_platform_dir_suffix(path) == str(path)


def test_apply_platform_dir_suffix_appends_platform_slash(
    monkeypatch,
    platform,
    platform_slash,
    raw_target_dir
):
    """When a Path.is_dir() returns True, a platform-appropriate suffix is added."""

    path = make_mock_path(raw_target_dir, is_dir=True)
    monkeypatch.setattr(Path, "resolve", lambda self: path)
    
    assert apply_platform_dir_suffix(path).endswith(platform_slash)

