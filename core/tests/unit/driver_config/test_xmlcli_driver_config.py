from collections import OrderedDict

from dtaf_core.lib.private.driver_config.xmlcli_driver_config import XmlcliDriverConfig
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
            <xmlcli>
                <sutospath>"/opt/APP/xmlcli/"</sutospath>
                <bios_cfgfilepath>C:\\biosxml\\</bios_cfgfilepath>
                <bios_cfgfilename>neoncity.cfg</bios_cfgfilename>
                <ip>10.190.179.22</ip>
                <user>root</user>
                <password>password</password>
            </xmlcli>
            """
        ),
        OrderedDict([('xmlcli', OrderedDict([('sutospath', '"/opt/APP/xmlcli/"'),
                                             ('bios_cfgfilepath', 'C:\\biosxml\\'),
                                             ('bios_cfgfilename', 'neoncity.cfg'),
                                             ('ip', '10.190.179.22'), ('user', 'root'),
                                             ('password', 'password')]))])
     ]
)


class TestXmlCliDriverConfig:
    def test_xmlcli_cfg_normal(self):
        for cfg in cfg_dict["normal"]:
            with DriverCfgFactory.create(cfg, Logs()) as cfg_model:  # type: XmlcliDriverConfig
                assert cfg_model.name
                assert cfg_model.sutospath
                assert cfg_model.bios_cfgfilename
                assert cfg_model.bios_cfgfilepath
                assert cfg_model.ip
                assert cfg_model.user
                assert cfg_model.password
