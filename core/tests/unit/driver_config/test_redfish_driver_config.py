from collections import OrderedDict

from dtaf_core.lib.private.driver_config.redfish_driver_config import RedfishDriverConfig
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
            <redfish>
                <ip>10.239.181.130</ip>
                <username>root</username>
                <password>0penBmc</password>
                <image_name_bmc>demo.rom</image_name_bmc>
                <image_path_bmc>xxxxx</image_path_bmc>
            </redfish>
            """
        ),
        OrderedDict([('redfish', OrderedDict(
            [('ip', '10.239.181.130'), ('username', 'root'), ('password', '0penBmc'), ('image_name_bmc', 'demo.rom'),
             ('image_path_bmc', 'xxxxx')]))])
    ]
)


class TestRedfishDriverConfig:
    def test_redfish_cfg_normal(self):
        for cfg in cfg_dict["normal"]:
            with DriverCfgFactory.create(cfg, Logs()) as cfg_model:  # type: RedfishDriverConfig
                assert cfg_model.name
                assert cfg_model.ip
                assert cfg_model.username
                assert cfg_model.password
                assert cfg_model.image_name
                assert cfg_model.image_path
