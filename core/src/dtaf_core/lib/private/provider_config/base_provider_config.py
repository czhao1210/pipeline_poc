from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element

import xmltodict

from dtaf_core.lib.private.driver_config.base_driver_config import BaseDriverConfig
from dtaf_core.lib.private.drivercfg_factory import DriverCfgFactory


class BaseProviderConfig(object):
    def __init__(self, cfg_opts, log):
        super(BaseProviderConfig, self).__init__()
        self._cfg = cfg_opts
        provider_name = list(dict(cfg_opts).keys())[0]
        self.__provider_name = provider_name.strip()
        self.__driver_cfg = DriverCfgFactory.create(
            cfg_opts=cfg_opts[provider_name][r"driver"],
            log=log)  # type: BaseDriverConfig

    def __enter__(self):
        """
        Enter resource context for this driver.

        :return: Resource to use (usually self)
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit resource context for this driver.

        :param exc_type: Exception type
        :param exc_val: Exception value
        :param exc_tb: Exception traceback
        :return: None
        """
        pass  # Note: DO NOT return a "True" value if you override this function. Otherwise, exceptions will be hidden!

    @property
    def provider_name(self):
        return self.__provider_name

    @property
    def driver_cfg(self):
        return self.__driver_cfg

    def to_dict(self):
        cfg = self._cfg
        print(self._cfg)
        if isinstance(cfg, Element):
            cfg = ET.tostring(cfg)
            cfg = xmltodict.parse(cfg)
        return cfg

    def to_xml(self):
        cfg = self._cfg
        if isinstance(cfg, dict):
            cfg = {self.provider_name: cfg}
            cfg = xmltodict.unparse(cfg)
            cfg = ET.fromstring(cfg)
        return cfg
