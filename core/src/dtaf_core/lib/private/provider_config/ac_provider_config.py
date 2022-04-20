from dtaf_core.lib.private.provider_config.base_provider_config import BaseProviderConfig
from dtaf_core.lib.config_file_constants import ConfigFileParameters
import xmltodict
from xml.etree.ElementTree import Element, tostring
import xml


class AcProviderConfig(BaseProviderConfig):
    def __init__(self, cfg_opts, log):
        super(AcProviderConfig, self).__init__(cfg_opts, log)
        self.__poweron_timeout = None
        self.__poweroff_timeout = None
        cfg_dict = dict(cfg_opts)
        if xml.etree.ElementTree.iselement(cfg_opts):
            cfg_dict = xmltodict.parse(tostring(cfg_opts))
        try:
            self.__poweron_timeout = float(cfg_dict["ac"]["timeout"]["power_on"])
        except KeyError as key_error:
            # timeout not found in configuration file
            self.__poweron_timeout = None
            raise key_error
        try:
            self.__poweroff_timeout = float(cfg_dict["ac"]["timeout"]["power_off"])
        except KeyError as key_error:
            # timeout not found in configuration file
            self.__poweroff_timeout = None
            raise key_error

    @property
    def poweron_timeout(self):
        return self.__poweron_timeout

    @property
    def poweroff_timeout(self):
        return self.__poweroff_timeout
