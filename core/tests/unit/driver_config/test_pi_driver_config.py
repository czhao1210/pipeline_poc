from collections import OrderedDict

from dtaf_core.lib.private.driver_config.pi_driver_config import PiDriverConfig
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
            <pi>
                            <ip>10.190.155.174</ip>
                            <port>80</port>
                            <proxy>http://child-prc.intel.com:913</proxy>
							<gpio_timeout>xxx</gpio_timeout>
							<gpio_pin_number>xxx</gpio_pin_number>
							<state>xxx</state>
							<image_name>xxx</image_name>
							<image_path>xxx</image_path>
                        </pi> 
            """
        ),
        OrderedDict([('pi', OrderedDict(
            [('ip', '10.190.155.174'), ('port', '80'), ('proxy', 'http://child-prc.intel.com:913'),
             ('gpio_timeout', 'xxx'), ('gpio_pin_number', 'xxx'), ('state', 'xxx'), ('image_name', 'xxx'),
             ('image_path', 'xxx')]))])
    ]
)


class TestPiDriverConfig:
    def test_banino_cfg_normal(self):
        for cfg in cfg_dict["normal"]:
            with DriverCfgFactory.create(cfg, Logs()) as cfg_model:  # type: PiDriverConfig
                assert cfg_model.name
                assert cfg_model.image_path
                assert cfg_model.image_name
                assert cfg_model.ip
                assert cfg_model.port
                assert cfg_model.proxy
                assert cfg_model.gpio_timeout
                assert cfg_model.gpio_number
                assert cfg_model.state
