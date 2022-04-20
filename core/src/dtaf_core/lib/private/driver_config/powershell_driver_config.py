from dtaf_core.lib.private.driver_config.base_driver_config import BaseDriverConfig


class PowershellDriverConfig(BaseDriverConfig):
    def __init__(self, cfg_opts, log):
        super(PowershellDriverConfig, self).__init__(cfg_opts, log)
        driver_name = list(cfg_opts.keys())[0]
        cfg_dict = dict(cfg_opts)[driver_name]
        self.__host_name = cfg_dict["host"]["name"]
        self.__host_username = cfg_dict["host"]["username"]
        self.__host_password = cfg_dict["host"]["password"]

    @property
    def host(self):
        return self.__host_name

    @property
    def username(self):
        return self.__host_username

    @property
    def password(self):
        return self.__host_password

