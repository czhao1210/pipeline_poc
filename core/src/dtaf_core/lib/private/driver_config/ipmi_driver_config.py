from dtaf_core.lib.private.driver_config.base_driver_config import BaseDriverConfig
from dtaf_core.lib.config_file_constants import ConfigFileParameters

class IpmiDriverConfig(BaseDriverConfig):
    def __init__(self, cfg_opts, log):
        super(IpmiDriverConfig, self).__init__(cfg_opts, log)
        try:
            driver_name = list(cfg_opts.keys())[0]
            self.__ip = cfg_opts[driver_name][r"ip"].strip()
            self.__username = cfg_opts[driver_name][r"username"].strip()
            self.__password = cfg_opts[driver_name][r"password"].strip()
        except KeyError as k_error:
            self.__ip=None
            self.__username=None
            self.__password=None

        try:
            self.__cmd = cfg_opts[driver_name][r"cmd"].strip()
        except:
            self.__cmd=None

    @property
    def cmd(self):
        return self.__cmd

    @property
    def ip(self):
        return self.__ip

    @property
    def username(self):
        return self.__username

    @property
    def password(self):
        return self.__password
