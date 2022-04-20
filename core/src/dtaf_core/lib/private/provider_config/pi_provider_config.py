from dtaf_core.lib.private.provider_config.base_provider_config import BaseProviderConfig

class PiProviderConfig(BaseProviderConfig):
    def __init__(self, cfg_opts, log):
        super(PiProviderConfig, self).__init__(cfg_opts, log)
        try:
            provider_name = list(cfg_opts.keys())[0]
            self.__ip = cfg_opts[provider_name][r"ip"].strip()
            self.__port = cfg_opts[provider_name][r"port"].strip()
            self.__proxy = cfg_opts[provider_name][r"proxy"].strip()
        except KeyError as key_err:
            self.__ip = None
            self.__prot = None
            self.__proxy = None

        try:
            self.__image_path = cfg_opts[provider_name][r"image_path"].strip()
        except KeyError as key_err:
            self.__image_path = None

        try:
            self.__image_name = cfg_opts[provider_name][r"image_name"].strip()
        except KeyError as key_err:
            self.__image_name = None
        

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
