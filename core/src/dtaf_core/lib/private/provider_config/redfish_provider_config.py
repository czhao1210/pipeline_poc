import xml
import xmltodict
from xml.etree.ElementTree import Element, tostring
from dtaf_core.lib.config_file_constants import ConfigFileParameters
from dtaf_core.lib.private.provider_config.base_provider_config import BaseProviderConfig
class RedfishProviderConfig(BaseProviderConfig):
    def __init__(self, cfg_opts, log):
        super(RedfishProviderConfig, self).__init__(cfg_opts, log)
        try:
            driver_name = list(cfg_opts.keys())[0]
            cfg_dict = dict(cfg_opts)
            self.__ip = cfg_dict[driver_name][r"ip"].strip()
            self.__username = cfg_dict[driver_name][r"username"].strip()
            self.__password = cfg_dict[driver_name][r"password"].strip()
        except KeyError as k_e:
            self.__ip=None
            self.__username=None
            self.__password=None

        try:
            self.__image_name = cfg_dict[driver_name][r"image_name_bmc"].strip()
        except KeyError as k_e:
            self.__image_name = None

        try:
            self.__image_path = cfg_dict[driver_name][r"image_path_bmc"].strip()
        except KeyError as attrib_err:
            self.__image_path = None

        try:
            self.__image_name_bios = cfg_dict[driver_name][r"image_name_bios"].strip()
        except Exception as ex:
            self.__image_name_bios = None
        try:
            self.__image_path_bios = cfg_dict[driver_name][r"image_path_bios"].strip()
        except Exception as ex:
            self.__image_path_bios = None

        try:
            self.__image_name_cpld = cfg_dict[driver_name][r"image_name_cpld"].strip()
        except Exception as ex:
            self.__image_name_cpld = None
        try:
            self.__image_path_cpld = cfg_dict[driver_name][r"image_path_cpld"].strip()
        except Exception as ex:
            self.__image_path_cpld = None

        try:
            self.__bmc_type = cfg_dict[driver_name][r"bmc_type"].strip()
        except Exception as ex:
            self.__bmc_type = None

    @property
    def ip(self):
        return self.__ip

    @property
    def username(self):
        return self.__username

    @property
    def password(self):
        return self.__password

    @property
    def image_name(self):
        return self.__image_name

    @property
    def image_path(self):
        return self.__image_path

    @property
    def image_name_bios(self):
        return self.__image_name_bios

    @property
    def image_path_bios(self):
        return self.__image_path_bios

    @property
    def image_name_cpld(self):
        return self.__image_name_cpld

    @property
    def image_path_cpld(self):
        return self.__image_path_cpld

    @property
    def bmc_type(self):
        if ((str(self.__bmc_type)).lower() in ["commercial", "dell", "thirdparty", "external","idrac","supermicron"]):
            self.__bmc_type = "commercial"
            return self.__bmc_type
        else:
            self.__bmc_type = "rvp"
            return self.__bmc_type

