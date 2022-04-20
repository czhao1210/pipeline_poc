from dtaf_core.lib.config_file_constants import ConfigFileParameters
from dtaf_core.lib.private.driver_config.base_driver_config import BaseDriverConfig


class Pei4DriverConfig(BaseDriverConfig):
    def __init__(self, cfg_opts, log):
        super(Pei4DriverConfig, self).__init__(cfg_opts, log)
        driver_name = list(cfg_opts.keys())[0]
        cfg_dict = dict(cfg_opts)
        self._path = cfg_dict[driver_name]["path"]
    @property
    def path(self):
        return self._path
