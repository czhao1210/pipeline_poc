from dtaf_core.lib.private.provider_config.base_provider_config import BaseProviderConfig
from dtaf_core.lib.config_file_constants import ConfigFileParameters

class YkushProviderConfig(BaseProviderConfig):
    def __init__(self, cfg_opts, log):
        super(YkushProviderConfig, self).__init__(cfg_opts, log)
        provider_name = list(cfg_opts.keys())[0]
        try:
            self._ykush_app_path = cfg_opts[provider_name][r"ykush_app_path"].strip()
        except KeyError as key_err:
            self._ykush_app_path = None

    @property
    def ykush_app_path(self):
        return self._ykush_app_path