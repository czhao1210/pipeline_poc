from dtaf_core.lib.private.drivercfg_factory import DriverCfgFactory
import xmltodict

from dtaf_core.lib.private.driver_config.ssh_driver_config import SshDriverConfig
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
            <ssh>
                            <credentials user="xxxx" password="xxxxx" jump_host="xxxxx" jump_user="xxxxx" jump_password="xxxxx" jump_auth="xx" />
                            <ipv4>10.13.168.111</ipv4>
                        </ssh>
            """
        ),
        xmltodict.parse("""
        
            <ssh>
                            <credentials user="xxxx" password="xxxxx" jump_host="xxxxx" jump_user="xxxxx" jump_password="xxxxx" jump_auth="xx" />
                            <ipv4>10.13.168.111</ipv4>
                        </ssh>
        """)
    ]
)


class TestRedfishDriverConfig:
    def test_banino_cfg_normal(self):
        for cfg in cfg_dict["normal"]:
            with DriverCfgFactory.create(cfg, Logs()) as cfg_model:  # type: SshDriverConfig
                assert cfg_model.name
                assert cfg_model.ip
                assert cfg_model.user
                assert cfg_model.password
                assert cfg_model.jump_host
                assert cfg_model.jump_user
                print(">>>", cfg_model.jump_auth)
                assert cfg_model.jump_auth
