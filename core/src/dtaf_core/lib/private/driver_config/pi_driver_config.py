from dtaf_core.lib.private.driver_config.base_driver_config import BaseDriverConfig
from dtaf_core.lib.config_file_constants import ConfigFileParameters

class PiDriverConfig(BaseDriverConfig):
    def __init__(self, cfg_opts, log):
        super(PiDriverConfig, self).__init__(cfg_opts, log)
        driver_name = list(cfg_opts.keys())[0]
        self.__ip = cfg_opts[driver_name][r"ip"].strip()
        try:
            self.__port = cfg_opts[driver_name][r"port"].strip()
        except:
            self.__port = None
        try:
            self.__proxy = cfg_opts[driver_name][r"proxy"].strip()
        except:
            self.__proxy = None
        try:
            self.__gpio_timeout = cfg_opts[driver_name][r"gpio_timeout"].strip()
            self.__gpio_pin_number = cfg_opts[driver_name][r"gpio_pin_number"].strip()
            self.__state = cfg_opts[driver_name][r"state"].strip()
        except:
            self.__gpio_timeout=None
            self.__gpio_number=None
            self.__state=None
        try:
            self.__image_name = cfg_opts[driver_name][r"image_name"].strip()
        except KeyError as attrib_err:
            self.__image_name = None

        try:
            self.__image_path = cfg_opts[driver_name][r"image_path"].strip()
        except KeyError as attrib_err:
            self.__image_path = None

        try:
            self.__password = cfg_opts[driver_name][r"password"].strip()
        except KeyError as attrib_err:
            self.__password = "intel"

        try:
            self.__username = cfg_opts[driver_name][r"username"].strip()
        except KeyError as attrib_err:
            self.__username = "pi"

        try:
            self.__type = cfg_opts[driver_name][r"type"].strip()
        except KeyError as attrib_err:
            self.__ = None

        try:
            self.__type = cfg_opts[driver_name][r"type"].strip()
        except KeyError as attrib_err:
            self.__type = None

        try:
            self.__type = cfg_opts[driver_name][r"type"].strip()
        except KeyError as attrib_err:
            self.__type = None

        try:
            self.__password = cfg_opts[driver_name][r"password"].strip()
        except KeyError as attrib_err:
            self.__password = "intel"

        try:
            self.__username = cfg_opts[driver_name][r"username"].strip()
        except KeyError as attrib_err:
            self.__username = "pi"

        try:
            self.__type = cfg_opts[driver_name][r"type"].strip()
        except KeyError as attrib_err:
            self.__type = None

    @property
    def image_path(self):
        return self.__image_path
    
    @property
    def image_name(self):
        return self.__image_name
       
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
    def gpio_timeout(self):
        return self.__gpio_timeout

    @property
    def gpio_number(self):
        return self.__gpio_pin_number

    @property
    def state(self):
        return self.__state

    @property
    def username(self):
        return self.__username

    @property
    def password(self):
        return self.__password

    @property
    def type(self):
        self.__type = self.__type.lower() if self.__type else None
        return self.__type
