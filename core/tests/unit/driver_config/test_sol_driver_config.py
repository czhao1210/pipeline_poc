from collections import OrderedDict
from dtaf_core.lib.private.drivercfg_factory import DriverCfgFactory
from dtaf_core.lib.private.driver_config.sol_driver_config import SolDriverConfig

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
            <sol>
                            <address>0.0.0.0</address>
                            <port>1101</port>
                            <timeout>5</timeout>
                            <credentials user="xxxx" password="xxxxx"/>
                        </sol>
            """
        ),
        OrderedDict([('sol', OrderedDict([('address', '0.0.0.0'), ('port', '1101'), ('timeout', '5'),
                                          ('credentials', OrderedDict([('@password', 'xxxxx'), ('@user', 'xxxx')]))]))])
    ]
)


class TestRedfishDriverConfig:
    def test_banino_cfg_normal(self):
        for cfg in cfg_dict["normal"]:
            with DriverCfgFactory.create(cfg, Logs()) as cfg_model:  # type: SolDriverConfig
                assert cfg_model.name
                assert cfg_model.address
                assert cfg_model.port
                assert cfg_model.timeout
                assert cfg_model.user
                assert cfg_model.password
