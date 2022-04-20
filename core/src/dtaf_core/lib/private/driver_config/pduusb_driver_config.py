from dtaf_core.lib.private.driver_config.base_driver_config import BaseDriverConfig
from dtaf_core.lib.config_file_constants import ConfigFileParameters


class PduusbDriverConfig(BaseDriverConfig):
    def __init__(self, cfg_opts, log):
        super(PduusbDriverConfig, self).__init__(cfg_opts, log)
        driver_name = list(cfg_opts.keys())[0]
        try:
            self.__pduusb_ac_port = cfg_opts[driver_name]["outlets"][ConfigFileParameters.XML_PATH_TO_OUTLETS]
            if len(self.__pduusb_ac_port) == 1:
                self.__pduusb_ac_port = int(self.__pduusb_ac_port)
            else:
                for i in range(0, len(self.__pduusb_ac_port)):
                    self.__pduusb_ac_port[i] = int(self.__pduusb_ac_port[i])
                out = str(self.__pduusb_ac_port).replace("[", '')
                self.__pduusb_ac_port = str(out).replace("]", '')
        except KeyError as k_e:
            log.error(k_e)
            self.__pduusb_ac_port = None

    @property
    def pduusb_ac_port(self):
        """
        Physical AC connection on belwin pdu (1-5)

        """
        return self.__pduusb_ac_port
