from dtaf_core.lib.private.driver_config.base_driver_config import BaseDriverConfig


class Rsc2DriverConfig(BaseDriverConfig):
    def __init__(self, cfg_opts, log):
        super(Rsc2DriverConfig, self).__init__(cfg_opts, log)
