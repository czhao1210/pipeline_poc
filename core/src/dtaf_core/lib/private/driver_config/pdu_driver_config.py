"""
pdu driver config
"""

from dtaf_core.lib.private.driver_config.base_driver_config import BaseDriverConfig
from dtaf_core.lib.config_file_constants import ConfigFileParameters


class PduDriverConfig(BaseDriverConfig):
    """
    pdu config
    """

    class GroupConfig(object):
        def __init__(self, onegroup):
            self.__onegroup = onegroup

        @property
        def ip(self):
            return self.__onegroup["ip"].strip() if "ip" in self.__onegroup.keys() else None

        @property
        def port(self):
            return self.__onegroup["port"].strip() if "port" in self.__onegroup.keys() else None

        @property
        def username(self):
            return self.__onegroup["username"].strip() if "username" in self.__onegroup.keys() else None

        @property
        def password(self):
            return self.__onegroup["password"].strip() if "password" in self.__onegroup.keys() else None

        @property
        def invoke_timeout(self):
            try:
                return int(self.__onegroup[r"timeout"]["invoke"].strip())
            except KeyError as e:
                return None

        @property
        def powerstate_timeout(self):
            try:
                return int(self.__onegroup[r"timeout"]["powerstate"].strip())
            except KeyError as e:
                return None

        @property
        def outlets(self):
            outlets = list()
            if isinstance(self.__onegroup["outlets"]["outlet"], str):
                return [self.__onegroup["outlets"]["outlet"].strip()]
            else:
                return self.__onegroup["outlets"]["outlet"]

    def __init__(self, cfg_opts, log):
        super(PduDriverConfig, self).__init__(cfg_opts, log)
        driver_name = list(cfg_opts.keys())[0]
        self.__brand = ""
        if "@brand" in cfg_opts[driver_name].keys():
            self.__brand = cfg_opts[driver_name]["@brand"].strip()
        if "groups" in cfg_opts[driver_name].keys():
            self.__parse_groups(cfg_opts[driver_name])
        else:
            self.__groups = [PduDriverConfig.GroupConfig(cfg_opts[driver_name])]

    def __parse_groups(self, groups_opts):
        groups = list()
        if isinstance(groups_opts["groups"]["group"], list):
            for g in groups_opts["groups"]["group"]:
                groups.append(PduDriverConfig.GroupConfig(g))
        else:
            groups.append(PduDriverConfig.GroupConfig(groups_opts["groups"]["group"]))
        self.__groups = groups

    @property
    def groups(self):
        return self.__groups

    @property
    def ip(self):
        '''
        host ip address
        :return:
        '''
        if self.__groups:
            return self.__groups[0].ip
        return self.__ip

    @property
    def port(self):
        '''
        host port
        :return:
        '''
        if self.__groups:
            return self.__groups[0].port
        return self.__port

    @property
    def username(self):
        '''
        login user
        :return:
        '''
        if self.__groups:
            return self.__groups[0].username
        return self.__username

    @property
    def password(self):
        '''
        login password
        :return:
        '''
        if self.__groups:
            return self.__groups[0].password
        return self.__password

    @property
    def invoke_timeout(self):
        '''
        wait invoke time
        :return:
        '''
        if self.__groups:
            return self.__groups[0].invoke_timeout
        return self.__invoke_timeout

    @property
    def powerstate_timeout(self):
        '''
        wait invoke time
        :return:
        '''
        if self.__groups:
            return self.__groups[0].powerstate_timeout
        return self.__powerstate_timeout

    @property
    def outlets(self):
        '''
        outlets groups
        :return:
        '''
        if self.__groups:
            return self.__groups[0].outlets
        if isinstance(self.__outlets, str):
            return [self.__outlets]
        return self.__outlets

    @property
    def brand(self):
        return self.__brand
