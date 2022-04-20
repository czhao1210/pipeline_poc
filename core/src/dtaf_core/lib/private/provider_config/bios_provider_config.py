from dtaf_core.lib.config_file_constants import ConfigFileParameters
from dtaf_core.lib.private.provider_config.base_provider_config import BaseProviderConfig

class BiosProviderConfig(BaseProviderConfig):
    def __init__(self, cfg_opts, log):
        super(BiosProviderConfig, self).__init__(cfg_opts, log)
        provider_name = list(cfg_opts.keys())[0]
        try:
            self.__sutospath = cfg_opts[provider_name]["sutospath"]
        except KeyError as e:
            self.__sutospath = ""
        try:
            self.__bios_cfgfilename = cfg_opts[provider_name][r"bios_cfgfilename"]
        except KeyError as e:
            self.__bios_cfgfilename = ""
        try:
            self.__bios_cfgfilepath = cfg_opts[provider_name][r"bios_cfgfilepath"]
        except KeyError as e:
            self.__bios_cfgfilepath = ""
        #print("cleared")

    def __enter__(self):
        """
        Enter resource context for this driver.

        :return: Resource to use (usually self)
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit resource context for this driver.

        :param exc_type: Exception type
        :param exc_val: Exception value
        :param exc_tb: Exception traceback
        :return: None
        """
        pass  # Note: DO NOT return a "True" value if you override this function. Otherwise, exceptions will be hidden!

    @property
    def sutospath(self):
        return self.__sutospath

    @property
    def bios_cfgfilename(self):
        return self.__bios_cfgfilename

    @property
    def bios_cfgfilepath(self):
        return self.__bios_cfgfilepath


