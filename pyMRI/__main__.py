from pyMRI.windowing import launch
from pyMRI.config import configure
from pyMRI.data_loading import get_scan_config, load_scan
from sys import argv

if __name__ == '__main__':
    mri_config = configure(*argv[1:])
    scan_config = get_scan_config(mri_config)
    launch(mri_config, scan_config)
