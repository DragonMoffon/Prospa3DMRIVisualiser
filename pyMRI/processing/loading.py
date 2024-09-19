from pathlib import Path

from pyMRI.processing.step import Step
from pyMRI.processing.data import FileData, Unit, Orientation

from pyMRI.loading.prospa import (
    ProspaData,
    ProspaParameters,
    ProspaDataLoader,
    ProspaParametersLoader,
)


class FileLoaderStep(Step[None, FileData]):

    def __init__(self, next_step: Step):
        super().__init__(next_step)
        self.data_path: str = ""
        self._data_loader: ProspaDataLoader = None

        self.parameter_path: str = ""
        self._parameter_loader: ProspaParametersLoader = None

        self.exclude_parameter_file: bool = False
        self.can_use_parameter_file: bool = True

        self.orient_override: Orientation = None
        self.dimension_override: tuple[int, int, int] = None
        self.unit_override: Unit = None

        self._ready = True

    def _recalculate(self, _input: None) -> FileData | None:
        # If the data path is invalid then we are done here
        if self.data_path is not None and (
            not Path(self.data_path).exists() or not Path(self.data_path).is_file()
        ):
            return

        # If there is no data path then use the dialog to find one
        # otherwise use the data path which should be valid at this point
        if self.data_path is None:
            self._data_loader = ProspaDataLoader.fetch()
        elif self._data_loader is None or self.data_path != self._data_loader.path:
            self._data_loader = ProspaDataLoader(self.data_path)

        # If the data loader failed to be created then we bounce
        if self._data_loader is None:
            return

        # Update the data path in the case we used the dialog
        self._ready = False
        self.data_path = str(self._data_loader.path)
        self._ready = True

        # load the data file
        data: ProspaData = self._data_loader.data

        # fill out dud arguments here incase the parameter file doesn't load
        orient = "xyz"
        count = data.count
        dimensions = (1.0, 1.0, 1.0)
        unit = Unit.MM

        # If we actually want to use the parameter file
        if not self.exclude_parameter_file:
            # If the parameter path is invalid then we are done here
            if self.parameter_path is not None and (
                not Path(self.parameter_path).exists()
                or not Path(self.parameter_path).is_file()
            ):
                return

            # If there is no parameter path use the dialog to find one
            # otheriwse use the parameter path which should be valid
            if self.parameter_path is None:
                self._parameter_loader = ProspaParametersLoader.fetch()
                self._ready = False
                self.unit_override = None
                self.orient_override = None
                self.dimension_override = None
                self._ready = True
            elif (
                self._parameter_loader is None
                or self.parameter_path != self._parameter_loader.path
            ):
                self._parameter_loader = ProspaParametersLoader(self.parameter_path)
                self._ready = False
                self.unit_override = None
                self.orient_override = None
                self.dimension_override = None
                self._ready = True

            # If the parameter file fails to load lets leave
            if self._parameter_loader is None:
                return

            # update the parameter path to update the path loaded
            self._ready = False
            self.parameter_path = str(self._parameter_loader.path)
            self._ready = True

            # load the parameter file
            parameters: ProspaParameters = self._parameter_loader.data

            # Get the actual values from the parameter file
            orient = parameters.orient
            count = (
                parameters.img_count,
                parameters.img_width,
                parameters.img_height,
            )
            dimensions = (parameters.phase_2, parameters.phase_1, parameters.read)

        # Use the override values if they have been set
        unit = unit if self.unit_override is None else self.unit_override
        orient = orient if self.orient_override is None else self.orient_override
        dimensions = (
            dimensions if self.dimension_override is None else self.dimension_override
        )

        return FileData(
            orient,
            dimensions,
            unit,
            count,
            data.data,
        )
