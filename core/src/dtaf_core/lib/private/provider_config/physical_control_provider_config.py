
from dtaf_core.lib.private.provider_config.base_provider_config import BaseProviderConfig
from dtaf_core.lib.config_file_constants import ConfigFileParameters
from xml.etree.ElementTree import Element, tostring
import xmltodict


class PhysicalControlProviderConfig(BaseProviderConfig):
    def __init__(self, cfg_opts, log):
        super(PhysicalControlProviderConfig, self).__init__(cfg_opts, log)
        cfg_dict = dict(cfg_opts)
        try:
            self.__usb_switch_timeout = int(cfg_dict["physical_control"]["timeout"]["usbswitch"])
        except KeyError as attrib_err:
            # timeout not found in configuration file
            self.__usb_switch_timeout = None

        try:
            self.__clear_cmos_timeout = int(cfg_dict["physical_control"]["timeout"]["clearcmos"])
        except KeyError as attrib_err:
            # timeout not found in configuration file
            self.__clear_cmos_timeout = None

        
    @property
    def usb_switch_timeout(self):
        return self.__usb_switch_timeout

    @property
    def clear_cmos_timeout(self):
        return self.__clear_cmos_timeout
