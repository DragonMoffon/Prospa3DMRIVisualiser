from pyMRI.windowing import launch
from pyMRI.config import configure
from pyMRI.data_loading import get_scan_config, load_scan
from sys import argv

if __name__ == '__main__':
    launch_config = configure(*argv[1:])
    launch(launch_config)
