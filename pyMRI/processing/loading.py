from pathlib import Path

from pyMRI.processing.step import Step
from pyMRI.processing.data import FileData

from pyMRI.loading.prospa import ProspaData, ProspaParameters, ProspaDataLoader, ProspaParametersLoader


class FileLoaderStep(Step[None, FileData]):

    def __init__(self, next_step: Step):
        super().__init__(next_step)
        self.data_path: str = None
        self._data_loader: ProspaDataLoader = None

        self.parameter_path: str = None
        self._parameter_loader: ProspaParametersLoader = None

    def _recalculate(self, _input: None) -> FileData | None:
        if self.data_path is not None and not Path(self.data_path).exists():
            return
        if self.parameter_path is not None and not Path(self.parameter_path).exists():
            return

        if self.data_path is None:
            self._data_loader = ProspaDataLoader.fetch()
        elif self._data_loader is None or self.data_path != self._data_loader.path:
            self._data_loader = ProspaDataLoader(self.data_path)
    
        data: ProspaData = self._data_loader.data

        if self.parameter_path is None:
            self._parameter_loader = ProspaParametersLoader.fetch()
        elif self._parameter_loader is None or self.parameter_path != self._parameter_loader.path:
            self._parameter_loader = ProspaParametersLoader(self.parameter_path)
   
        parameters: ProspaParameters = self._parameter_loader.data

        return FileData(
            parameters.orient,
            (parameters.phase_2, parameters.phase_1, parameters.read),
            (parameters.img_count, parameters.img_width, parameters.img_height),
            data.data
        )