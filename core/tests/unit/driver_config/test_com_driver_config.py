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
            <com>
                <port>COM100</port>
                <baudrate>115200</baudrate>
                <timeout>5</timeout>
            </com>
            """
        ),
        OrderedDict([('com', OrderedDict([('port', 'COM100'), ('baudrate', '115200'), ('timeout', '5')]))])
    ]
)


class TestComDriverConfig:
    def test_banino_cfg_normal(self):
        for cfg in cfg_dict["normal"]:
            with DriverCfgFactory.create(cfg, Logs()) as cfg_model:  # type: ComDriverConfig
                assert cfg_model.name
                assert cfg_model.port
                assert cfg_model.baudrate
                assert cfg_model.timeout
