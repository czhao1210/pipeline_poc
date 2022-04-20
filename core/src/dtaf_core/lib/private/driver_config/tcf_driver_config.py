from dtaf_core.lib.private.driver_config.base_driver_config import BaseDriverConfig


class TcfDriverConfig(BaseDriverConfig):
    # Set by TCF
    _targets = None
    _interconnects = None

    def __init__(self, cfg_opts, log):
        super(TcfDriverConfig, self).__init__(cfg_opts, log)

    @property
    def targets(self):
        return self._targets

    @property
    def interconnects(self):
        return self._interconnects
