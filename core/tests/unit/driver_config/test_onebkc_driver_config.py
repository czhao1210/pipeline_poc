from collections import OrderedDict

from dtaf_core.lib.private.driver_config.onebkc_driver_config import OnebkcDriverConfig
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
            <onebkc>
                            <credentials user="xxxx" password="xxxxx"/>
                            <kit path="" name=""/>
                        </onebkc>
            """
        ),
        OrderedDict([('onebkc', OrderedDict([('credentials', OrderedDict([('@password', 'xxxxx'), ('@user', 'xxxx')])),
                                             ('kit', OrderedDict([('@name', ''), ('@path', '')]))]))])
    ]
)


class TestOnebkcDriverConfig:
    def test_banino_cfg_normal(self):
        for cfg in cfg_dict["normal"]:
            with DriverCfgFactory.create(cfg, Logs()) as cfg_model:  # type: OnebkcDriverConfig
                assert cfg_model.name
