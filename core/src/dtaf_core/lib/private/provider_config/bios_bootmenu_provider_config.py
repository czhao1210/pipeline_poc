from dtaf_core.lib.private.provider_config.base_provider_config import BaseProviderConfig
from xml.etree.ElementTree import SubElement, ElementTree, Element
from xml.etree.ElementTree import Element, tostring
import xmltodict
import xml


class BiosBootmenuProviderConfig(BaseProviderConfig):
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
        select_item = cfg["bios_bootmenu"][tag][r"@select_item"]
        path_list = list()
        return BiosBootmenuProviderConfig.Entry(select_item=select_item, path=path_list)

    def __init__(self, cfg_opts, log):
        super(BiosBootmenuProviderConfig, self).__init__(cfg_opts, log)
        cfg_dict = dict(cfg_opts)
        self.__screen = cfg_dict["bios_bootmenu"].get('screen')
        try:
            self.__width = int(self.__screen['@width'])
            self.__height = int(self.__screen['@height'])
        except Exception as ex:
            self.__width = 80
            self.__height = 24
        if xml.etree.ElementTree.iselement(cfg_opts):
            cfg_dict = xmltodict.parse(tostring(cfg_opts))
        self.__efishell_entry = None
        try:
            self.__efishell_entry = self.__parse_entry(cfg=cfg_dict, tag=r"efishell_entry")
        except TypeError as e:
            self.__efishell_entry = None

    @property
    def efishell_entry(self):
        return self.__efishell_entry

    @efishell_entry.setter
    def efishell_entry(self, value):
        self.__efishell_entry = value

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height
