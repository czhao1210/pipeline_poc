from dtaf_core.lib.private.provider_config.base_provider_config import BaseProviderConfig
from dtaf_core.lib.config_file_constants import ConfigFileParameters

class PduApcProviderConfig(BaseProviderConfig):
    def __init__(self, cfg_opts, log):
        super(PduApcProviderConfig, self).__init__(cfg_opts, log)
        try:
            cfg_dict = dict(cfg_opts)
            provide_name = list(cfg_dict.keys())[0]
            self.__ip = cfg_opts[provide_name][r"ip"].strip()
            self.__port = cfg_opts[provide_name][r"port"].strip()
            self.__username = cfg_opts[provide_name][r"username"].strip()
            self.__password = cfg_opts[provide_name][r"password"].strip()
            self.__outlets = cfg_opts[provide_name]["outlets"][ConfigFileParameters.XML_PATH_TO_OUTLETS]
        except KeyError as k_e:
            self.__ip = None
            self.__port = None
            self.__username = None
            self.__password = None
            self.__outlets = None
        try:
            self.__invoke_timeout = int(cfg_opts[provide_name][r"timeout"]["invoke"].strip())
        except KeyError:
            self.__invoke_timeout = 0
        except TypeError:
            self.__invoke_timeout = 0

        try:
            self.__powerstate_timeout = int(cfg_opts[provide_name][r"timeout"]["powerstate"].strip())
        except KeyError:
            self.__powerstate_timeout = 0
        except TypeError:
            self.__powerstate_timeout = 0

    @property
    def ip(self):
        '''
        host ip address
        :return:
        '''
        return self.__ip

    @property
    def port(self):
        '''
        host port
        :return:
        '''
        return self.__port

    @property
    def username(self):
        '''
        login user
        :return:
        '''
        return self.__username

    @property
    def password(self):
        '''
        login password
        :return:
        '''
        return self.__password

    @property
    def invoke_timeout(self):
        '''
        wait invoke time
        :return:
        '''
        return self.__invoke_timeout

    @property
    def powerstate_timeout(self):
        '''
        wait invoke time
        :return:
        '''
        return self.__powerstate_timeout

    @property
    def outlets(self):
        '''
        outlets groups
        :return:
        '''
        if isinstance(self.__outlets, str):
            return [self.__outlets]
        return self.__outlets
