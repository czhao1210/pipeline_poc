from collections import OrderedDict

from dtaf_core.lib.private.driver_config.com_driver_config import ComDriverConfig
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
            <wsol>
                <ip>xxx.xxx.xxx.xxx</ip>
                <port>console0</port>
                <timeout>10</timeout>
                <credentials user="user" password="password"/>
            </wsol>
            """
        ),
        OrderedDict([('wsol', OrderedDict([('ip', 'xxx.xxx.xxx.xxx'), ('port', 'console0'), ('timeout', '10'), ('credentials', OrderedDict([('@user', 'user'), ('@password', 'password')]))]))])
    ]
)


class TestWsolDriverConfig:
    def test_wsol_cfg_normal(self):
        for cfg in cfg_dict["normal"]:
            with DriverCfgFactory.create(cfg, Logs()) as cfg_model:  # type: ComDriverConfig
                assert cfg_model.name
                assert cfg_model.port
                assert cfg_model.ip
                assert cfg_model.timeout
