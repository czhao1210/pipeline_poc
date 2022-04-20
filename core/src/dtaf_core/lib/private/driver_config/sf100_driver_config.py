from dtaf_core.lib.private.driver_config.base_driver_config import BaseDriverConfig


class Sf100DriverConfig(BaseDriverConfig):
    def __init__(self, cfg_opts, log):
        super(Sf100DriverConfig, self).__init__(cfg_opts, log)
        driver_name = list(cfg_opts.keys())[0]
        cfg_dict = dict(cfg_opts)
        self.cli_path = cfg_dict[driver_name]["@cli_path"]
