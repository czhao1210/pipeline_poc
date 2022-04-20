from collections import OrderedDict

from dtaf_core.lib.private.driver_config.ipmi_driver_config import IpmiDriverConfig
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
            <ipmi>
                    <ip>10.239.181.70</ip>
                    <username>root</username>
                    <password>0penBmc1</password>
                    <cmd>ipmitool.exe</cmd>
            </ipmi>
            """
        ),
        OrderedDict([('ipmi', OrderedDict(
            [('ip', '10.239.181.70'), ('username', 'root'), ('password', '0penBmc1'), ('cmd', 'ipmitool.exe')]))])
    ]
)


class TestIpmiDriverConfig:
    def test_banino_cfg_normal(self):
        for cfg in cfg_dict["normal"]:
            with DriverCfgFactory.create(cfg, Logs()) as cfg_model:  # type: IpmiDriverConfig
                assert cfg_model.name
                assert cfg_model.cmd
                assert cfg_model.ip
                assert cfg_model.username
                assert cfg_model.password
