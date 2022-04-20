from dtaf_core.lib.private.driver_config.base_driver_config import BaseDriverConfig
from dtaf_core.lib.config_file_constants import ConfigFileParameters

class BaninoDriverConfig(BaseDriverConfig):
    def __init__(self, cfg_opts, log):
        super(BaninoDriverConfig, self).__init__(cfg_opts, log)
        driver_name = list(cfg_opts.keys())[0]
        try:
            self._banino_dll_path = cfg_opts[driver_name][r"banino_dll_path"].strip()
        except:
            self._banino_dll_path = r"C:\banino\code\BaninoControlCenter\x64\ladybird.dll"
        try:
            self._banino_power_cmd = cfg_opts[driver_name][r"banino_power_cmd"].strip()
        except KeyError as key_err:
            self._banino_power_cmd = None
        try:
            self._ladybird_driver_serial = cfg_opts[driver_name][r"ladybird_driver_serial"].strip()
        except KeyError as key_err:
            self._banino_self._ladybird_driver_serial = None
        try:
            self._rasp = cfg_opts[driver_name][r"rasp"].strip()
        except KeyError as key_err:
            self._rasp = None
        try:
            self._num_banino = cfg_opts[driver_name][r"banino_count"].strip()
        except KeyError as key_err:
            self._num_banino = 1

        try:
            self.__image_path = cfg_opts[driver_name][r"image_path"].strip()
        except KeyError as key_err:
            self.__image_path = None

        try:
            self.__image_name = cfg_opts[driver_name][r"image_name"].strip()
        except KeyError as key_err:
            self.__image_name = None

        try:
            self.__image_path_bmc = cfg_opts[driver_name][r"image_path_bmc"].strip()
        except KeyError as key_err:
            self.__image_path_bmc = None

        try:
            self.__image_name_bmc = cfg_opts[driver_name][r"image_name_bmc"].strip()
        except KeyError as key_err:
            self.__image_name_bmc = None

        try:
            self.__chip_verification_ifwi =  cfg_opts[driver_name][r"chip_verification_ifwi"].strip()
        except Exception as key_err:
            self.__chip_verification_ifwi = None

        try:
            self.__chip_verification_bmc =  cfg_opts[driver_name][r"chip_verification_bmc"].strip()
        except Exception as key_err:
            self.__chip_verification_bmc = None

    @property
    def banino_dll_path(self):
        return self._banino_dll_path

    @property
    def banino_num(self):
        return self._num_banino

    @property
    def banino_power_cmd(self):
        return self._banino_power_cmd
    
    @property
    def ladybird_driver_serial(self):
        return self._ladybird_driver_serial

    @property
    def image_path(self):
        return self.__image_path

    @property
    def image_name(self):
        return self.__image_name

    @property
    def image_path_bmc(self):
        return self.__image_path_bmc

    @property
    def image_name_bmc(self):
        return self.__image_name_bmc

    @property
    def chip_verification_ifwi(self):
        if ((str(self.__chip_verification_ifwi)).lower() in ["true", "yes", "on", "enable"]):
            self._chip_verification_ifwi = True
            return self._chip_verification_ifwi
        else:
            self._chip_verification_ifwi = False
            return self._chip_verification_ifwi

    @property
    def chip_verification_bmc(self):
        if ((str(self.__chip_verification_bmc)).lower() in ["true", "yes", "on", "enable"]):
            self._chip_verification_bmc = True
            return self._chip_verification_bmc
        else:
            self._chip_verification_bmc = False
            return self._chip_verification_bmc

    @property
    def rasp(self):
        if ((str(self._rasp)).lower() in ["true", "yes", "on", "enable"]):
            self._rasp = True
        else:
            self._rasp = False
        return self._rasp