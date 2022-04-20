from collections import OrderedDict

from dtaf_core.lib.private.driver_config.pdupi_driver_config import PdupiDriverConfig
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
            <pdupi>
                        <ip>10.190.155.147</ip>
                        <port>80</port>
                        <proxy>http://child-prc.intel.com:913</proxy>
                        <channel>ch1</channel>
                        <username>admin</username>
                        <password>intel@123</password>
                        <masterkey>smartrpipdu</masterkey>
                    </pdupi>
            """
        ),
        OrderedDict([('pdupi', OrderedDict(
            [('ip', '10.190.155.147'), ('port', '80'), ('proxy', 'http://child-prc.intel.com:913'), ('channel', 'ch1'),
             ('username', 'admin'), ('password', 'intel@123'), ('masterkey', 'smartrpipdu')]))])
    ]
)


class TestPdupiDriverConfig:
    def test_banino_cfg_normal(self):
        for cfg in cfg_dict["normal"]:
            with DriverCfgFactory.create(cfg, Logs()) as cfg_model:  # type: PdupiDriverConfig
                assert cfg_model.name
                assert cfg_model.ip
                assert cfg_model.port
                assert cfg_model.proxy
                assert cfg_model.username
                assert cfg_model.password
                assert cfg_model.masterkey
                assert cfg_model.channel
