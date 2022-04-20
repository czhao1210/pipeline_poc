from dtaf_core.lib.config_file_constants import ConfigFileParameters
from dtaf_core.lib.private.driver_config.base_driver_config import BaseDriverConfig


class KeysightDriverConfig(BaseDriverConfig):
    def __init__(self, cfg_opts, log):
        super(KeysightDriverConfig, self).__init__(cfg_opts, log)
        driver_name = list(cfg_opts.keys())[0]
        cfg_dict = dict(cfg_opts)
        self._platform_dir = cfg_dict[driver_name]["platform_dir"]
        self._exerciser_dir = cfg_dict[driver_name]["exerciser_dir"]
        self._module = int(cfg_dict[driver_name]["module"])
        self._port = int(cfg_dict[driver_name]["port"])

    @property
    def platform_dir(self):
        return self._platform_dir

    @property
    def exerciser_dir(self):
        return self._exerciser_dir

    @property
    def module(self):
        return self._module

    @property
    def port(self):
        return self._port
