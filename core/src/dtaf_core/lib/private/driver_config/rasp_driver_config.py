from dtaf_core.lib.private.driver_config.base_driver_config import BaseDriverConfig


class RaspDriverConfig(BaseDriverConfig):
    def __init__(self, cfg_opts, log):
        super(RaspDriverConfig, self).__init__(cfg_opts, log)
        driver_name = list(cfg_opts.keys())[0]
        cfg_dict = dict(cfg_opts)[driver_name]
        self.__systemid = cfg_dict[r"systemid"].strip()
        self.__entry = cfg_dict[r"entry"].strip()
        self.__token = cfg_dict[r"token"].strip()

    @property
    def systemid(self):
        return self.__systemid

    @property
    def entry(self):
        return self.__entry

    @property
    def token(self):
        return self.__token

