from dtaf_core.lib.private.driver_config.base_driver_config import BaseDriverConfig
from dtaf_core.lib.config_file_constants import ConfigFileParameters

class TTKDriverConfig(BaseDriverConfig):
    def __init__(self, cfg_opts, log):
        super(TTKDriverConfig, self).__init__(cfg_opts, log)
        driver_name = list(cfg_opts.keys())[0]
        try:
            self.__localhost = cfg_opts[driver_name][r"localhost"].strip()
        except:
            self.__localhost = "127.0.0.1"

    @property
    def localhost(self):
        return self.__localhost
