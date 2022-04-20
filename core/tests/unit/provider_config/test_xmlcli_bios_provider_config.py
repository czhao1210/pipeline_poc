from collections import OrderedDict

from dtaf_core.lib.private.driver_config.xmlcli_driver_config import XmlcliDriverConfig
from dtaf_core.lib.private.provider_config.bios_provider_config import BiosProviderConfig
from dtaf_core.lib.private.providercfg_factory import ProviderCfgFactory

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
            <bios>
                    <driver>
                        <xmlcli>
                            <sutospath>"/opt/APP/xmlcli/"</sutospath>
                            <bios_cfgfilepath>C:\\biosxml\\</bios_cfgfilepath>
                            <bios_cfgfilename>neoncity.cfg</bios_cfgfilename>
                            <ip>10.190.179.22</ip>
                            <user>root</user>
                            <password>password</password>
                        </xmlcli>
                    </driver>					
            </bios>
            """
        ),
        OrderedDict([('bios',
                      OrderedDict([('driver',
                                    OrderedDict([('xmlcli', OrderedDict([('sutospath', '"/opt/APP/xmlcli/"'),
                                                                         ('bios_cfgfilepath', 'C:\\biosxml\\'),
                                                                         ('bios_cfgfilename', 'neoncity.cfg'),
                                                                         ('ip', '10.190.179.22'),
                                                                         ('user', 'root'),
                                                                         ('password', 'password')]))]))]))])

     ]
)


class TestXmlCliBiosProviderConfig:
    def test_xmlcli_bios_cfg_normal(self):
        for cfg in cfg_dict["normal"]:
            with ProviderCfgFactory.create(cfg, Logs()) as cfg_model:  # type: BiosProviderConfig
                driver_cfg = cfg_model.driver_cfg # type: XmlcliDriverConfig
                assert driver_cfg.sutospath is not None
                assert driver_cfg.password is not None
                assert driver_cfg.user is not None
                assert driver_cfg.name
                assert driver_cfg.bios_cfgfilename
                assert driver_cfg.bios_cfgfilepath
                assert driver_cfg.ip
