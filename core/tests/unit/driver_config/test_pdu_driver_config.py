ASSUME = True


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
            <pdu brand="raritan" model="px-5052R">
                            <ip>10.190.249.196</ip>
                            <port>22</port>
                            <username>admin</username>
                            <password>intel@123</password>
                            <timeout>15</timeout>
                            <outlets>
								<outlet>1</outlet>
                                <outlet>2</outlet>
                            </outlets>
                       </pdu>
            """
        ),
    ]
)


class TestPduDriverConfig:
    def test_banino_cfg_normal(self):
        for cfg in cfg_dict["normal"]:
            with DriverCfgFactory.create(cfg, Logs()) as cfg_model:  # type: PduDriverConfig
                assert cfg_model.ip
                assert cfg_model.port
                assert cfg_model.username
                assert cfg_model.password
                assert isinstance(cfg_model.outlets, list)
                assert cfg_model.outlets


import six

from dtaf_core.lib.private.drivercfg_factory import DriverCfgFactory
from dtaf_core.lib.private.driver_config.pdu_driver_config import PduDriverConfig

ASSUME = True

if six.PY2:
    pass

if six.PY3 or six.PY34:
    pass

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
            <pdu brand="raritan" model="px-5052R">
                            <ip>10.190.249.196</ip>
                            <port>22</port>
                            <username>admin</username>
                            <password>intel@123</password>
                            <timeout>15</timeout>
                            <outlets>
								<outlet>1</outlet>
                                <outlet>2</outlet>
                            </outlets>
                       </pdu>
            """
        ),
    ]
)


class TestPduDriverConfig:
    def test_banino_cfg_normal(self):
        for cfg in cfg_dict["normal"]:
            with DriverCfgFactory.create(cfg, Logs()) as cfg_model:  # type: PduDriverConfig
                assert cfg_model.name
                assert cfg_model.ip
                assert cfg_model.port
                assert cfg_model.username
                assert cfg_model.password
                assert isinstance(cfg_model.outlets, list)
                assert cfg_model.outlets
