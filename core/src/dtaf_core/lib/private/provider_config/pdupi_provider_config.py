from dtaf_core.lib.private.provider_config.base_provider_config import BaseProviderConfig
from dtaf_core.lib.config_file_constants import ConfigFileParameters

class PdupiProviderConfig(BaseProviderConfig):
    def __init__(self, cfg_opts, log):
        super(PdupiProviderConfig, self).__init__(cfg_opts, log)
        try:
            cfg_dict = dict(cfg_opts)
            provide_name = list(cfg_dict.keys())[0]
            self.__ip = cfg_dict[provide_name]["ip"].strip()
            self.__port = cfg_dict[provide_name]["port"].strip()
            self.__proxy = cfg_dict[provide_name]["proxy"].strip()
            self.__username = cfg_dict[provide_name]["username"].strip()
            self.__password = cfg_dict[provide_name]["password"].strip()
            self.__masterkey = cfg_dict[provide_name]["masterkey"].strip()
            self.__channel = cfg_dict[provide_name]["channel"].strip()
        except AttributeError as attrib_err:
            self.__ip=None
            self.__port=None
            self.__proxy=None
            self.__username=None
            self.__password=None
            self.__masterkey=None
            self.__channel=None
        

    @property
    def ip(self):
        return self.__ip

    @property
    def port(self):
        return self.__port

    @property
    def proxy(self):
        return self.__proxy
    
    @property
    def user_name(self):
        return self.__username

    @property
    def password(self):
        return self.__password

    @property
    def masterkey(self):
        return self.__masterkey

    @property
    def channel(self):
        return self.__channel
