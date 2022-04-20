from collections import OrderedDict

from dtaf_core.lib.private.driver_config.sf100_driver_config import Sf100DriverConfig
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
            <sf100 cli_path="C:\Program Files (x86)\DediProg\SF Programmer\">
                            <pch name="SF106223" chip="MX66L51235F" />
                            <bmc name="SF113876" chip="MX66L1G45G" />
                        </sf100>
            """
        ),
        OrderedDict([('sf100', OrderedDict([('@cli_path', 'C:\\Program Files (x86)\\DediProg\\SF Programmer'),
                                            ('pch', OrderedDict([('@chip', 'MX66L51235F'), ('@name', 'SF106223')])),
                                            ('bmc', OrderedDict([('@chip', 'MX66L1G45G'), ('@name', 'SF113876')]))]))])
    ]
)


class TestRedfishDriverConfig:
    def test_banino_cfg_normal(self):
        for cfg in cfg_dict["normal"]:
            with DriverCfgFactory.create(cfg, Logs()) as cfg_model:  # type: Sf100DriverConfig
                assert cfg_model.name
                assert cfg_model.cli_path
