from collections import OrderedDict

from dtaf_core.lib.private.driver_config.pythonsv_driver_config import PythonsvDriverConfig
from dtaf_core.lib.private.drivercfg_factory import DriverCfgFactory

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


cfg_dict = dict(
    normal=[
        ET.fromstring(
            """
            <pythonsv>
                <unlocker>C:\PushUtil\PushUtil.exe</unlocker>
                <debugger_interface_type>ITP</debugger_interface_type>
                <silicon>
                    <cpu_family>SKX</cpu_family>
                    <pch_family>LBG</pch_family>
                </silicon>
            </pythonsv>
            """
        ),
        OrderedDict([('pythonsv', OrderedDict(
            [('unlocker', 'C:\\PushUtil\\PushUtil.exe'), ('debugger_interface_type', 'ITP'),
             ('silicon', OrderedDict([('cpu_family', 'SKX'), ('pch_family', 'LBG')]))]))])
    ]
)


class TestPythonsvDriverConfig:
    def test_banino_cfg_normal(self):
        for cfg in cfg_dict["normal"]:
            with DriverCfgFactory.create(cfg, Logs()) as cfg_model:  # type: PythonsvDriverConfig
                assert cfg_model.name
                assert cfg_model.unlocker
                assert cfg_model.silicon_cpu_family
                assert cfg_model.silicon_pch_family
