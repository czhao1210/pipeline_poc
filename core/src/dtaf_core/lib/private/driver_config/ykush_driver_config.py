from dtaf_core.lib.private.driver_config.base_driver_config import BaseDriverConfig
from dtaf_core.lib.config_file_constants import ConfigFileParameters

class YkushDriverConfig(BaseDriverConfig):
    def __init__(self, cfg_opts, log):
        super(YkushDriverConfig, self).__init__(cfg_opts, log)
        try:
            driver_name = list(cfg_opts.keys())[0]
            self._ykush_app_path = cfg_opts[driver_name][r"ykush_app_path"].strip()
        except KeyError as key_err:
            self._ykush_app_path = None

    @property
    def ykush_app_path(self):
        return self._ykush_app_path
