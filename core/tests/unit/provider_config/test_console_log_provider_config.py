from collections import OrderedDict

from dtaf_core.lib.private.providercfg_factory import ProviderCfgFactory

ASSUME = True

from dtaf_core.lib.private.provider_config.console_log_provider_config import ConsoleLogProviderConfig

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
    console_log=[
        ET.fromstring(
            """
            <console_log>
                    <runwith>xxx</runwith>
                    <logpath>C:\\temp\logs</logpath>
                    <driver>
                        <sol>
                            <address>0.0.0.0</address>
                            <port>1101</port>
                            <timeout>5</timeout>
                            <credentials user="xxxx" password="xxxxx"/>
                        </sol>
                    </driver>
                </console_log>
            """
        ),
        OrderedDict([('console_log', OrderedDict([('runwith', 'xxx'), ('logpath', 'C:\\temp\\logs'), ('driver',
                                                                                                      OrderedDict([(
                                                                                                                   'sol',
                                                                                                                   OrderedDict(
                                                                                                                       [
                                                                                                                           (
                                                                                                                           'address',
                                                                                                                           '0.0.0.0'),
                                                                                                                           (
                                                                                                                           'port',
                                                                                                                           '1101'),
                                                                                                                           (
                                                                                                                           'timeout',
                                                                                                                           '5'),
                                                                                                                           (
                                                                                                                           'credentials',
                                                                                                                           OrderedDict(
                                                                                                                               [
                                                                                                                                   (
                                                                                                                                   '@password',
                                                                                                                                   'xxxxx'),
                                                                                                                                   (
                                                                                                                                   '@user',
                                                                                                                                   'xxxx')]))]))]))]))])
    ]
)


class TestSetupmenuProviderConfig:
    def test_console_log_provider_cfg_normal(self):
        for cfg in cfg_dict["console_log"]:
            with ProviderCfgFactory.create(cfg, Logs()) as cfg_model:  # type: ConsoleLogProviderConfig
                driver_cfg = cfg_model.driver_cfg
                assert cfg_model.provider_name
                assert cfg_model.logpath_local
                assert cfg_model.runwith_framework
                for k, v in cfg_model.__dict__.items():
                    print(k, v)
                    assert v is not None
                for k, v in driver_cfg.__dict__.items():
                    print(k, v)
                    assert v is not None
