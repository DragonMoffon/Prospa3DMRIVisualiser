import numpy as np
from tkinter import filedialog
from os.path import exists
from typing import TYPE_CHECKING

from pyMRI.config import MRIConfig, LaunchConfig
from pyMRI.data_loading import ScanConfig

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

        self._original_scan: ScanConfig = None
        self._scan_config: ScanConfig = None

        self._raw_read_data: np.ndarray = None

        """
        self._scan_images = load_scan(mri_config, scan_config)  
        self._scan_data = np.fft.ifftshift(self._scan_images, [-2])
        # for idx in range(0, scan_config.phase_2_count):
        #    img = self._scan_images[idx]
        #    # self._scan_data[idx] = img
        #    self._scan_data[idx] = np.fft.fftshift(np.fft.ifft2(np.fft.ifftshift(img, axes=[-2, -1]), norm='ortho'), axes=[-2, -1])
        #    # self._scan_data[idx] = np.fft.ifft2(img, norm='ortho')
        """

    def initialise(self):
        if self._launch_config.path is None:
            self.win.push_warning(
                GuiWarning("No Selected File", "pyMRI was launched without an input file path", WarningMode.INFO,
                           continue_override="Select", cancel_override="Quit",
                           continue_callback=self.load_data_dialog, cancel_callback=self.win.close)
            )
        else:
            self.load_data()

    @property
    def mri_config(self):
        return self._mri_config

    @property
    def scan_config(self):
        return self._scan_config

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
        if not (data_file and acqu_file) and not self._launch_config.path:
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
        elif (data_file and acqu_file) and self._launch_config.path:
            self.win.push_warning(
                GuiWarning(
                    "Invalid Data loading",
                    "pyMRI was given to many file options to know how to load data.",
                    WarningMode.ERROR,
                    continue_override="Try Again",
                    cancel_override="Quit",
                    continue_callback=self.load_data(),
                    cancel_callback=self.win.close
                )
            )
            return

        if not data_file:
            if exists(self._launch_config.path + (self._launch_config.data_name or "data.3d")):
                data_file = self._launch_config.path + (self._launch_config.data_name or "data.3d")
            elif exists(self._launch_config.path + (self._launch_config.data_name or "data.2d")):
                data_file = self._launch_config.path + (self._launch_config.data_name or "data.2d")
            elif exists(self._launch_config.path + (self._launch_config.data_name or "data.1d")):
                data_file = self._launch_config.path + (self._launch_config.data_name or "data.1d")
            else:
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

        if not acqu_file:
            acqu_file = self._launch_config.path + (self._launch_config.data_name or "acqu.par")
            if not exists(acqu_file):
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

        print(data_file, acqu_file)

    # Processing Operations

    # Filtering Operations

    # Visual Operations

    # Camera Operations

