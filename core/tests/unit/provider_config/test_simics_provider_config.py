from collections import OrderedDict

from dtaf_core.lib.private.providercfg_factory import ProviderCfgFactory

ASSUME = True

from dtaf_core.lib.private.provider_config.simics_provider_config import SimicsProviderConfig

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
                <simics>
                    <driver>
                        <com>
                            <port>COM21</port>
                            <baudrate>115200</baudrate>
                            <timeout>5</timeout>
                        </com>
                    </driver>
                    <telnet_port>10</telnet_port>
                    <workspace>10</workspace>
                    <simics_path>10</simics_path>
                    <serial_log>10</serial_log>
                </simics>
""")


class TestSuites:
    def test_cfg_normal(self):
        with ProviderCfgFactory.create(cfg, Logs()) as cfg_model:  # type: SimicsProviderConfig
            assert cfg_model.provider_name
            assert cfg_model.telnet_port
            assert cfg_model.serial_log
            assert cfg_model.workspace
            assert cfg_model.simics_path
