from dtaf_core.lib.private.driver_config.ssh_driver_config import SshDriverConfig
from dtaf_core.lib.private.provider_config.sut_os_provider_config import SutOsProviderConfig
from dtaf_core.lib.private.providercfg_factory import ProviderCfgFactory

ASSUME = True
import xmltodict

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
                <sut_os name="Linux" subtype="RHEL" version="7.6" kernel="3.10">
                    <shutdown_delay>5.0</shutdown_delay>
                    <driver>
                        <ssh>
                            <credentials user="root" password="password"/>
                            <ipv4>10.190.191.121</ipv4>
                        </ssh>
                    </driver>
                </sut_os>
            """
        ),
        xmltodict.parse("""
                        <sut_os name="Linux" subtype="RHEL" version="7.6" kernel="3.10">
                    <shutdown_delay>5.0</shutdown_delay>
                    <driver>
                        <ssh>
                            <credentials user="root" password="password"/>
                            <ipv4>10.190.191.121</ipv4>
                        </ssh>
                    </driver>
                </sut_os>
        """)

    ]
)


class TestSshSutOSProviderConfig:
    def test_ssh_sut_os_cfg_normal(self):
        for cfg in cfg_dict["normal"]:
            with ProviderCfgFactory.create(cfg, Logs()) as cfg_model:  # type: SutOsProviderConfig
                assert cfg_model.provider_name
                assert cfg_model.driver_cfg
                assert cfg_model.os_kernel
                assert cfg_model.os_subtype
                assert cfg_model.os_type
                assert cfg_model.os_version
                assert cfg_model.shutdown_delay
                driver_cfg = cfg_model.driver_cfg  # type: SshDriverConfig
                assert driver_cfg.password is not None
                assert driver_cfg.user is not None
                assert driver_cfg.name
                assert driver_cfg.jump_auth is None
                assert driver_cfg.jump_host is None
                assert driver_cfg.jump_user is None
                assert driver_cfg.ip
