import numpy as np
from tkinter import filedialog
from os.path import exists
from typing import TYPE_CHECKING

from pyMRI.config import LaunchConfig
from pyMRI.data_loading import MRIConfig, load_scan, get_scan_config

from pyMRI.gui.warning import GuiWarning, WarningMode

from pyMRI.rendering.voxel import VoxelRenderer

from arcade import get_window

if TYPE_CHECKING:
    from pyMRI.windowing.window import MRIWindow


class MRI:

    def __init__(self, launch_config: LaunchConfig, voxel_renderer: VoxelRenderer):
        self.win: MRIWindow = get_window()

        self._launch_config: LaunchConfig = launch_config
        self._voxel_renderer: VoxelRenderer = voxel_renderer

        self._original_mri: MRIConfig = None
        self._mri_config: MRIConfig = None

        self._raw_read_data: np.ndarray = None
    

    def initialise(self):
        self.win.push_warning(
            GuiWarning("No File Loaded", "Please Select a File", WarningMode.INFO,
                    continue_override="Select", cancel_override="Quit",
                    continue_callback=self.load_data_dialog, cancel_callback=self.win.close)
        )

    @property
    def mri_config(self):
        return self._mri_config

    # File
    def load_data_dialog(self):
        files: dict[str, str] = {"data": None, "acqu": None}

        def _load_data():
            self.load_data(files['data'], files['acqu'])

        def _get_par():
            files['acqu'] = filedialog.askopenfilename(title="Select a parameter file",
                                                       filetypes=[("Prospa Parameter file", "*.par"),
                                                                  ("All Files", "*.*")])
            _load_data()

        files['data'] = filedialog.askopenfilename(title="Select a data file",
                                                   filetypes=[("Prospa 3D", "*.3d"), ("Prospa 2D", "*.2d"),
                                                              ("Prospa 1D", "*.1d"), ("All Files", "*.*")])
        if files['data'][-3:] not in {".3d", ".2d", ".1d"}:
            self.win.push_warning(
                GuiWarning(
                    "Non-Prospa Data",
                    "The data file chosen is not a prospa file, would you like to continue?",
                    WarningMode.WARNING,
                    cancel_override="Quit",
                    continue_callback=_get_par,
                    cancel_callback=self.win.close
                )
            )
        else:
            _get_par()

    def load_data(self, data_file: str = None, acqu_file: str = None):
        if not (data_file and acqu_file):
            self.win.push_warning(
                GuiWarning(
                    "Invalid Data loading",
                    "pyMRI tried to load data, but was given invalid files.",
                    WarningMode.ERROR,
                    continue_override="Try Again",
                    cancel_override="Quit",
                    continue_callback=self.load_data_dialog,
                    cancel_callback=self.win.close
                )
            )
            return

        if data_file[-3:] not in {".3d", ".2d", ".1d"}:
            self.win.push_warning(
                GuiWarning(
                    "Invalid Data loading",
                    "pyMRI does not currently support non-Prospa data",
                    WarningMode.ERROR,
                    continue_override="Try Again",
                    cancel_override="Quit",
                    continue_callback=self.load_data_dialog,
                    cancel_callback=self.win.close
                )
            )
            return

        if acqu_file[-4:] != ".par":
            self.win.push_warning(
                GuiWarning(
                    "Invalid Data loading",
                    "Unrecognised parameter file.",
                    WarningMode.ERROR,
                    continue_override="Try Again",
                    cancel_override="Quit",
                    continue_callback=self.load_data_dialog,
                    cancel_callback=self.win.close
                )
            )
            return

        mri_config = get_scan_config(acqu_file)

        self._mri_config = self._original_mri = mri_config
        self._raw_read_data = load_scan(mri_config, data_file)
        
        self._voxel_renderer.update_gpu_data(self._raw_read_data, self._mri_config)

    # Processing Operations

    # Filtering Operations

    # Visual Operations

    # Camera Operations

