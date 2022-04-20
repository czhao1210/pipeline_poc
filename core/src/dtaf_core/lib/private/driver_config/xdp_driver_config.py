from dtaf_core.lib.private.driver_config.base_driver_config import BaseDriverConfig


class XdpDriverConfig(BaseDriverConfig):
    def __init__(self, cfg_opts, log):
        super(XdpDriverConfig, self).__init__(cfg_opts, log)
        driver_name = list(cfg_opts.keys())[0]
        cfg_dict = dict(cfg_opts)
        self._debugger_type = cfg_dict[driver_name]["@type"]

    @property
    def debugger_type(self):
        return self._debugger_type
