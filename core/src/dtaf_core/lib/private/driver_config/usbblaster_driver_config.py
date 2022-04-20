from dtaf_core.lib.private.driver_config.base_driver_config import BaseDriverConfig
from dtaf_core.lib.config_file_constants import ConfigFileParameters
from xml.etree.ElementTree import Element, tostring
import xml
import xmltodict


class UsbblasterDriverConfig(BaseDriverConfig):
    def __init__(self, cfg_opts, log):
        super(UsbblasterDriverConfig, self).__init__(cfg_opts, log)
        cfg_dict = dict(cfg_opts)
        if xml.etree.ElementTree.iselement(cfg_opts):
            cfg_dict = xmltodict.parse(tostring(cfg_opts))
        try:
            self.__cpld_application_path = cfg_opts['usbblaster'][r"cpld_application_path"]
        except AttributeError as attrib_err:
            self.__cpld_application_path = None

        try:
            self.__primary_image_path = cfg_opts['usbblaster'][r"primary_image_path"]
        except AttributeError as attrib_err:
            self.__primary_image_path = None

        try:
            self.__primary_image_name = cfg_opts['usbblaster'][r"primary_image_name"]
        except AttributeError as attrib_err:
            self.__primary_image_name = None

        try:
            self.__secondary_image_path = cfg_opts['usbblaster'][r"secondary_image_path"]
        except AttributeError as attrib_err:
            self.__secondary_image_path = None

        try:
            self.__secondary_image_name = cfg_opts['usbblaster'][r"secondary_image_name"]
        except AttributeError as attrib_err:
            self.__secondary_image_name = None

    @property
    def cpld_application_path(self):
        return self.__cpld_application_path

    @property
    def primary_image_path(self):
        return self.__primary_image_path

    @property
    def primary_image_name(self):
        return self.__primary_image_name

    @property
    def secondary_image_path(self):
        return self.__secondary_image_path

    @property
    def secondary_image_name(self):
        return self.__secondary_image_name
