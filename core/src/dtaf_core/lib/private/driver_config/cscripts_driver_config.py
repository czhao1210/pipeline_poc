from dtaf_core.lib.config_file_constants import ConfigFileParameters
from dtaf_core.lib.private.driver_config.base_driver_config import BaseDriverConfig
from xml.etree.ElementTree import Element, tostring
import xmltodict


class CscriptsDriverConfig(BaseDriverConfig):

    def __init__(self, cfg_opts, log):
        super(CscriptsDriverConfig, self).__init__(cfg_opts, log)
        driver_name = list(cfg_opts.keys())[0]
        self._debugger_type = cfg_opts[driver_name][ConfigFileParameters.XML_PATH_TO_SILICON_REG_DEBUG_TYPE]
        self._silicon_cpu_family = cfg_opts[driver_name]["silicon"]["cpu_family"]
        self._silicon_pch_family = cfg_opts[driver_name]["silicon"]["pch_family"]

    @property
    def debugger_type(self):
        return self._debugger_type

    @property
    def silicon_cpu_family(self):
        return self._silicon_cpu_family

    @property
    def silicon_pch_family(self):
        return self._silicon_pch_family
