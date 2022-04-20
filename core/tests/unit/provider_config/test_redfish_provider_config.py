from collections import OrderedDict

from dtaf_core.lib.private.providercfg_factory import ProviderCfgFactory

ASSUME = True

from dtaf_core.lib.private.provider_config.redfish_provider_config import RedfishProviderConfig

import time
from xml.etree import ElementTree as ET


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


cfg = ET.fromstring("""
<redfish>
                    <driver>
                        <com>
                            <port>COM21</port>
                            <baudrate>115200</baudrate>
                            <timeout>5</timeout>
                        </com>
                    </driver>
                    <image_path_bmc>xxx</image_path_bmc>
                </redfish>
""")


class TestSuites:
    def test_cfg_normal(self):
        with ProviderCfgFactory.create(cfg, Logs()) as cfg_model:
            driver_cfg = cfg_model.driver_cfg
            assert cfg_model.provider_name
            assert cfg_model.ip == None
            assert cfg_model.username == None
            assert cfg_model.password == None
            assert cfg_model.image_path
            assert cfg_model.image_name == None
            assert cfg_model.image_path
            assert cfg_model.image_name_bios == None
            assert cfg_model.image_path_cpld == None
            assert cfg_model.image_name_cpld == None
