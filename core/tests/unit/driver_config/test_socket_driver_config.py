from collections import OrderedDict

from dtaf_core.lib.private.driver_config.socket_driver_config import SocketDriverConfig
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
            <socket>
                            <ip>127.0.0.1</ip>
                            <port>5555</port>
                            <bufsize>1030</bufsize>
                        </socket>
            """
        ),
        OrderedDict([('socket', OrderedDict([('ip', '127.0.0.1'), ('port', '5555'), ('bufsize', '1030')]))])
    ]
)


class TestRedfishDriverConfig:
    def test_banino_cfg_normal(self):
        for cfg in cfg_dict["normal"]:
            with DriverCfgFactory.create(cfg, Logs()) as cfg_model:  # type: SocketDriverConfig
                assert cfg_model.name
                assert cfg_model.ip_address
                assert cfg_model.port
                assert cfg_model.buffer_size
