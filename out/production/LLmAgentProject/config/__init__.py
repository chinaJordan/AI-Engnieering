from .EnvConfig import initConfig
from .EnvConfig import *

initConfig()


class GlobalConfig:
    DEEP_SEEK_KEY = DEEP_SEEK_KEY
    ENV = ENV


global_config = GlobalConfig()
