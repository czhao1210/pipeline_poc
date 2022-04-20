from dtaf_core.lib.private.driver_config.usbblaster_driver_config import UsbblasterDriverConfig
from dtaf_core.lib.private.drivercfg_factory import DriverCfgFactory

ASSUME = True

import time
from xml.etree import ElementTree as ET
import xmltodict


class Logs:
    def debug(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass


def power_on_states_timeout():
    time.sleep(10)
    return r'On'


def power_off_states_timeout():
    time.sleep(10)
    return r'Off'


cfg_dict = dict(
    normal=[
        ET.fromstring(
            """
            <usbblaster>
                            <cpld_application_path>C:\intelFPGA_pro\\18.1\qprogrammer\\bin64\</cpld_application_path>
                            <primary_image_path>C:\cpld_frimware\</primary_image_path>
                            <primary_image_name>main.pof</primary_image_name>
                            <secondary_image_path>C:\cpld_frimware\</secondary_image_path>
                            <secondary_image_name>second.pof</secondary_image_name>
                        </usbblaster>
            """
        ),
        xmltodict.parse(
            """
            <usbblaster>
                            <cpld_application_path>C:\intelFPGA_pro\\18.1\qprogrammer\\bin64\</cpld_application_path>
                            <primary_image_path>C:\cpld_frimware\</primary_image_path>
                            <primary_image_name>main.pof</primary_image_name>
                            <secondary_image_path>C:\cpld_frimware\</secondary_image_path>
                            <secondary_image_name>second.pof</secondary_image_name>
                        </usbblaster>
            """
        )
    ]
)


class TestRedfishDriverConfig:
    def test_banino_cfg_normal(self):
        for cfg in cfg_dict["normal"]:
            with DriverCfgFactory.create(cfg, Logs()) as cfg_model:  # type: UsbblasterDriverConfig
                assert cfg_model.name
                assert cfg_model.cpld_application_path
                assert cfg_model.primary_image_path
                assert cfg_model.primary_image_name
                assert cfg_model.secondary_image_path
                assert cfg_model.secondary_image_name
