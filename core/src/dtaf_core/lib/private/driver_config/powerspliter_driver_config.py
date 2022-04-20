from dtaf_core.lib.private.driver_config.base_driver_config import BaseDriverConfig
from dtaf_core.lib.config_file_constants import ConfigFileParameters

class PowerspliterDriverConfig(BaseDriverConfig):
    def __init__(self, cfg_opts, log):
        super(PowerspliterDriverConfig, self).__init__(cfg_opts, log)
        driver_name = list(cfg_opts.keys())[0]
        try:
            self._powerspliter_dll_path = cfg_opts[driver_name][r"Powerspliter_dll_path"].strip()
        except:
            self._powerspliter_dll_path = r"C:\powerspliter\USBPower.dll"

        try:
            self._powerspliter_driver_serial = cfg_opts[driver_name][r"powerspliter_serial"].strip()
        except KeyError as key_err:
            self._powerspliter_driver_serial  = None

        try:
            self._outlets = cfg_opts[driver_name]["outlets"][ConfigFileParameters.XML_PATH_TO_OUTLETS]
        except KeyError as key_err:
            self._outlets = None

    @property
    def powerspliter_dll_path(self):
        return self._powerspliter_dll_path
    
    @property
    def powerspliter_serial(self):
        return self._powerspliter_driver_serial

    @property
    def outlets(self):
        if isinstance(self._outlets, str):
            return [self._outlets]
        return self._outlets
