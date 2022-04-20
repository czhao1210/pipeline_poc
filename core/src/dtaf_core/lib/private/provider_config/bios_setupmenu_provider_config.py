from dtaf_core.lib.private.provider_config.base_provider_config import BaseProviderConfig
from xml.etree.ElementTree import SubElement, ElementTree, Element
from xml.etree.ElementTree import Element, tostring
import xmltodict
import xml

"""
                    <efishell_entry select_item="Launch EFI Shell">
                        <path>
                            <node>Setup Menu</node>
                            <node>Boot Manager</node>
                        </path>
                    </efishell_entry>
                    <continue select_item="Continue"/>
                    <reset press_key="\\33R\\33r\\33R" parse="False"/>
"""


class BiosSetupmenuProviderConfig(BaseProviderConfig):
    class Entry(object):
        def __init__(self, select_item, path):
            self.__select_time = select_item
            self.__path = path

        @property
        def select_item(self):
            return self.__select_time

        @property
        def path(self):
            return self.__path

    class Reset(object):
        def __init__(self, press_key, parse):
            self.__press_key = press_key
            self.__parse = parse

        @property
        def press_key(self):
            return self.__press_key

        @property
        def parse(self):
            return self.__parse

    def __parse_entry(self, cfg, tag):
        # type: (dict, str) -> Entry
        select_item = cfg["bios_setupmenu"][tag][r"@select_item"]
        path_list = list()
        nodes = list()
        if r"path" in cfg["bios_setupmenu"][tag].keys():
            nodes = cfg["bios_setupmenu"][tag][r"path"]["node"]  # type: list[str]
        for n in nodes:
            path_list.append([n, None])
        return BiosSetupmenuProviderConfig.Entry(select_item=select_item, path=path_list)

    def __init__(self, cfg_opts, log):
        super(BiosSetupmenuProviderConfig, self).__init__(cfg_opts, log)
        self.__efishell_entry = None
        self.__continue = None
        cfg_dict = dict(cfg_opts)
        self.__screen = cfg_dict["bios_setupmenu"].get('screen')
        try:
            self.__width = int(self.__screen['@width'])
            self.__height = int(self.__screen['@height'])
        except Exception as ex:
            self.__width = 80
            self.__height = 24
        if xml.etree.ElementTree.iselement(cfg_opts):
            cfg_dict = xmltodict.parse(tostring(cfg_opts))
        try:
            self.__efishell_entry = self.__parse_entry(cfg=cfg_dict, tag=r"efishell_entry")
        except KeyError as e:
            self.__efishell_entry = None
        try:
            self.__continue = self.__parse_entry(cfg=cfg_dict, tag=r"continue")
        except KeyError as e:
            self.__continue = None
        try:
            press_key = cfg_dict["bios_setupmenu"]["reset"]["@press_key"]
            parse = eval(cfg_dict["bios_setupmenu"]["reset"]["@parse"])
            self.__reset = BiosSetupmenuProviderConfig.Reset(press_key=press_key, parse=parse)
        except TypeError as type_err:
            self.__reset = None
        except KeyError as key_err:
            self.__reset = None

    @property
    def efishell_entry(self):
        return self.__efishell_entry

    @property
    def continue_entry(self):
        return self.__continue

    @property
    def reset_entry(self):
        return self.__reset

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height
