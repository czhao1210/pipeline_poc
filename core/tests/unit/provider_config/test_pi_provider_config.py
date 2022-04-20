from dtaf_core.lib.private.providercfg_factory import ProviderCfgFactory

ASSUME = True

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
<pi>
                    <driver>
                        <com>
                            <port>COM21</port>
                            <baudrate>115200</baudrate>
                            <timeout>5</timeout>
                        </com>
                    </driver>
                </pi>
""")


class TestSuites:
    def test_cfg_normal(self):

        with ProviderCfgFactory.create(cfg, Logs()) as cfg_model:
            driver_cfg = cfg_model.driver_cfg
            assert cfg_model.provider_name
            assert cfg_model.image_path == None
            assert cfg_model.image_name == None
            assert cfg_model.ip == None
            try:
                assert cfg_model.port
            except AttributeError:
                pass
            assert cfg_model.proxy == None
