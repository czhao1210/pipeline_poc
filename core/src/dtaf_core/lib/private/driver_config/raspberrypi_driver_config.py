from dtaf_core.lib.config_file_constants import ConfigFileParameters
from dtaf_core.lib.private.driver_config.base_driver_config import BaseDriverConfig

class RaspberryPiDriverConfig(BaseDriverConfig):
    def __init__(self, cfg_opts, log):
        super(RaspberryPiDriverConfig, self).__init__(cfg_opts, log)
        driver_name = list(cfg_opts.keys())[0]
        self.__ac_gpio_phase = int(cfg_opts.find(r"ac_gpio_phase").text.strip())
        self.__ac_gpio_neutral = int(cfg_opts.find(r"ac_gpio_neutral").text.strip())
        self.__dc_power_gpio = int(cfg_opts.find(r"dc_power_gpio").text.strip())
        self.__reboot_gpio = int(cfg_opts.find(r"reboot_gpio").text.strip())
        self.__dc_detection_gpio = int(cfg_opts.find(r"dc_detection_gpio").text.strip())
        self.__ac_detection_gpio = int(cfg_opts.find(r"ac_detection_gpio").text.strip())
        self.__clear_cmos_gpio = int(cfg_opts.find(r"clear_cmos_gpio").text.strip())
        self.__usb_switch_phase = int(cfg_opts.find(r"usb_switch_phase").text.strip())
        self.__usb_switch_datapos = int(cfg_opts.find(r"usb_switch_datapos").text.strip())
        self.__usb_switch_dataneg = int(cfg_opts.find(r"usb_switch_dataneg").text.strip())
        self.__s3_detection_gpio = int(cfg_opts.find(r"s3_detection_gpio").text.strip())
        self.__s4_detection_gpio = int(cfg_opts.find(r"s4_detection_gpio").text.strip())

    @property
    def ac_gpio_phase(self):
        return self.__ac_gpio_phase

    @property
    def ac_gpio_neutral(self):
        return self.__ac_gpio_neutral

    @property
    def dc_power_gpio(self):
        return self.__dc_power_gpio

    @property
    def reboot_gpio(self):
        return  self.__reboot_gpio

    @property
    def dc_detection_gpio(self):
        return self.__dc_detection_gpio

    @property
    def ac_detection_gpio(self):
        return self.__ac_detection_gpio

    @property
    def clear_cmos_gpio(self):
        return self.__clear_cmos_gpio

    @property
    def usb_switch_phase(self):
        return self.__usb_switch_phase

    @property
    def usb_switch_datapos(self):
        return self.__low_memory_voltage

    @property
    def usb_switch_dataneg(self):
        return self.__usb_switch_dataneg

    @property
    def s3_detection_gpio(self):
        return self.__s3_detection_gpio

    @property
    def s4_detection_gpio(self):
        return self.__s4_detection_gpio
