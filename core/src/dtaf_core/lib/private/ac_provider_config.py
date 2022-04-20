from dtaf_core.lib.private.provider_config.base_provider_config import BaseProviderConfig
from xml.etree import ElementTree
import xmltodict

class AcProviderConfig(BaseProviderConfig):
    def __init__(self, cfg_opts, log):
        super(AcProviderConfig, self).__init__(cfg_opts, log)
        self.__poweron_timeout = None
        self.__poweroff_timeout = None
        cfg_dict = cfg_opts
        if ElementTree.iselement(cfg_opts):
            cfg_dict = xmltodict.parse(cfg_opts)
        try:
            self.__poweron_timeout = float(cfg_dict["ac"][r"timeout"]["power_on"].strip())
        except AttributeError as attrib_err:
            # timeout not found in configuration file
            self.__poweron_timeout = None
        try:
            self.__poweroff_timeout = float(cfg_dict["ac"][r"timeout"]["power_off"].strip())
        except AttributeError as attrib_err:
            # timeout not found in configuration file
            self.__poweroff_timeout = None

    @property
    def poweron_timeout(self):
        return self.__poweron_timeout

    @property
    def poweroff_timeout(self):
        return self.__poweroff_timeout
