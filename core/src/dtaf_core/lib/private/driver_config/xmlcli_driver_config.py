from dtaf_core.lib.config_file_constants import ConfigFileParameters
from dtaf_core.lib.private.driver_config.base_driver_config import BaseDriverConfig
from xml.etree.ElementTree import Element, tostring
import xmltodict
import xml

class XmlcliDriverConfig(BaseDriverConfig):
    def __init__(self, cfg_opts, log):
        super(XmlcliDriverConfig, self).__init__(cfg_opts, log)
        cfg_dict = dict()
        if xml.etree.ElementTree.iselement(cfg_opts):
            cfg_dict = xmltodict.parse(tostring(cfg_opts))
        else:
            cfg_dict = cfg_opts
        print(cfg_dict)
        self.__sutospath = cfg_dict["xmlcli"]["sutospath"]
        self.__bios_cfgfilename = cfg_dict["xmlcli"]["bios_cfgfilename"]
        self.__bios_cfgfilepath = cfg_dict["xmlcli"]["bios_cfgfilepath"]
        self.__ip = cfg_dict["xmlcli"]["ip"]
        self.__user = cfg_dict["xmlcli"]["user"]
        self.__password = cfg_dict["xmlcli"]["password"]
        try:
            self.__root_privilege = cfg_dict["xmlcli"]["root_privilege"]
        except KeyError as e:
            self.__root_privilege = False

        try:
            self.__port = cfg_dict["xmlcli"]["port"]
        except KeyError as e:
            self.__port = 22  # if no special port defined, use SSH default port 22

        try:
            self.__python_path = cfg_dict["xmlcli"]["python_path"]
        except KeyError as e:
            self.__python_path = None

        if "/" in self.__sutospath:
            Environment = "Linux"
            self.__python_path = "python"
        else:
            Environment = "Windows"
            if self.__python_path:
                self.__python_path = "cd "+str(self.__python_path)+" && python"
            else:
                self.__python_path ="cd C:\Program Files\Python37\ && python"
    @property
    def sutospath(self):
        return self.__sutospath

    @property
    def bios_cfgfilename(self):
        return self.__bios_cfgfilename

    @property
    def bios_cfgfilepath(self):
        return self.__bios_cfgfilepath

    @property
    def ip(self):
        return self.__ip

    @property
    def port(self):
        return self.__port

    @property
    def user(self):
        return self.__user

    @property
    def password(self):
        return self.__password

    @property
    def root_privilege(self):
        if ((str(self.__root_privilege)).lower() in ["true", "yes", "on", "enable"]):
            self.__root_privilege = True
            return  self.__root_privilege
        else:
            return self.__root_privilege

    @property
    def python_path(self):
        return self.__python_path