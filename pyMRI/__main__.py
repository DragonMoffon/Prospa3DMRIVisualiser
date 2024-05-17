from pyMRI.windowing import launch
from pyMRI.config import configure
from sys import argv

if __name__ == '__main__':
    config = configure(*argv[1:])
    launch(config)
