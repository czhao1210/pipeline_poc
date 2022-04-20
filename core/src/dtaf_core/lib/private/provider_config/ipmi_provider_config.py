from dtaf_core.lib.private.provider_config.base_provider_config import BaseProviderConfig
from dtaf_core.lib.config_file_constants import ConfigFileParameters
from xml.etree.ElementTree import Element, tostring
import xmltodict

class IpmiProviderConfig(BaseProviderConfig):
    def __init__(self, cfg_opts, log):
        super(IpmiProviderConfig, self).__init__(cfg_opts, log)
        try:
            cfg_dict = dict(cfg_opts)
            provide_name = list(cfg_dict.keys())[0]
            self.__cmd = cfg_dict[provide_name][r"cmd"].strip()
            self.__ip = cfg_dict[provide_name][r"ip"].strip()
            self.__username = cfg_dict[provide_name][r"username"].strip()
            self.__password = cfg_dict[provide_name][r"password"].strip()
        except AttributeError as attrib_err:
            self.__cmd=None
            self.__ip=None
            self.__username=None
            self.__password=None

    @property
    def cmd(self):
        return self.__cmd

    @property
    def ip(self):
        return self.__ip

    @property
    def user_name(self):
        return self.__username

    @property
    def password(self):
        return self.__password
