from dtaf_core.lib.private.provider_config.base_provider_config import BaseProviderConfig
from dtaf_core.lib.config_file_constants import ConfigFileParameters

class TTKProviderConfig(BaseProviderConfig):
    def __init__(self, cfg_opts, log):
        super(TTKProviderConfig, self).__init__(cfg_opts, log)
        driver_name = list(cfg_opts.keys())[0]
        try:
            self.__localhost = cfg_opts[driver_name][r"localhost"].strip()
        except:
            self.__localhost = "127.0.0.1"

    @property
    def state(self):
        return self.__localhost
