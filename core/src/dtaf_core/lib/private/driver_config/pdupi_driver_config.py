from dtaf_core.lib.private.driver_config.base_driver_config import BaseDriverConfig
from dtaf_core.lib.config_file_constants import ConfigFileParameters

class PdupiDriverConfig(BaseDriverConfig):
    def __init__(self, cfg_opts, log):
        super(PdupiDriverConfig, self).__init__(cfg_opts, log)
        provider_name = list(cfg_opts.keys())[0]
        try:
            self.__ip = cfg_opts[provider_name][r"ip"].strip()
            self.__port = cfg_opts[provider_name][r"port"].strip()
            self.__proxy = cfg_opts[provider_name][r"proxy"].strip()
            self.__username = cfg_opts[provider_name][r"username"].strip()
            self.__password = cfg_opts[provider_name][r"password"].strip()
            self.__masterkey = cfg_opts[provider_name][r"masterkey"].strip()
            self.__channel = cfg_opts[provider_name][r"channel"].strip()
        except AttributeError as attrib_err:
            raise
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
    def username(self):
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
