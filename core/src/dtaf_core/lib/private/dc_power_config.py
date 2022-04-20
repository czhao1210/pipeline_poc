from dtaf_core.lib.private.provider_config.base_provider_config import BaseProviderConfig


class DcPowerConfig(BaseProviderConfig):
    def __init__(self, cfg_opts, log):
        super(DcPowerConfig, self).__init__(cfg_opts, log)
        self.__poweron_timeout = None
        self.__poweroff_timeout = None
        try:
            self.__poweron_timeout = float(cfg_opts.find(r"timeout/power_on").text.strip())
        except AttributeError as attrib_err:
            # timeout not found in configuration file
            self.__poweron_timeout = None
        try:
            self.__poweroff_timeout = float(cfg_opts.find(r"timeout/power_off").text.strip())
        except AttributeError as attrib_err:
            # timeout not found in configuration file
            self.__poweroff_timeout = None

    @property
    def poweron_timeout(self):
        return self.__poweron_timeout

    @property
    def poweroff_timeout(self):
        return self.__poweroff_timeout
