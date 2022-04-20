from dtaf_core.lib.private.provider_config.base_provider_config import BaseProviderConfig
import xmltodict
from xml.etree.ElementTree import Element, tostring
import xml

class DcProviderConfig(BaseProviderConfig):
    def __init__(self, cfg_opts, log):
        super(DcProviderConfig, self).__init__(cfg_opts, log)
        self.__poweron_timeout = None
        self.__poweroff_timeout = None
        cfg_dict = dict(cfg_opts)
        if xml.etree.ElementTree.iselement(cfg_opts):
            cfg_dict = xmltodict.parse(tostring(cfg_opts))
        try:
            self.__poweron_timeout = float(cfg_dict["dc"]["timeout"]["power_on"])
        except KeyError as error:
            # timeout not found in configuration file
            self.__poweron_timeout = None
            raise error
        try:
            self.__poweroff_timeout = float(cfg_dict["dc"]["timeout"]["power_off"])
        except KeyError as error:
            # timeout not found in configuration file
            self.__poweroff_timeout = None
            raise error
        try:
            self.__power_off_button_down = float(cfg_dict["dc"]["timeout"]["power_off_button_down"])
        except KeyError as error:
            # timeout not found in configuration file
            self.__power_off_button_down = 5

    @property
    def poweron_timeout(self):
        return self.__poweron_timeout

    @property
    def poweroff_timeout(self):
        return self.__poweroff_timeout

    @property
    def power_off_button_down(self):
        return self.__power_off_button_down
