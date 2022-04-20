from collections import OrderedDict

from dtaf_core.lib.private.providercfg_factory import ProviderCfgFactory

ASSUME = True

from dtaf_core.lib.private.provider_config.ipmi_provider_config import IpmiProviderConfig

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
                <ipmi>
                    <driver>
                        <ipmi>
                            <cmd>xxx</cmd>
                            <ip>xxx</ip>
                            <username>xxx</username>
                            <password>xxx</password>
                        </ipmi>
                    </driver>
                    <cmd>xxx</cmd>
                    <ip>xxx</ip>
                    <username>xxx</username>
                    <password>xxx</password>
                </ipmi>
""")


class TestSuites:
    def test_cfg_normal(self):
        with ProviderCfgFactory.create(cfg, Logs()) as cfg_model:  # type: IpmiProviderConfig
            assert cfg_model.provider_name
            assert cfg_model.cmd
            assert cfg_model.ip
            assert cfg_model.user_name
            assert cfg_model.password
