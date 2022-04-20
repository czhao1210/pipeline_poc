from collections import OrderedDict

from dtaf_core.lib.private.providercfg_factory import ProviderCfgFactory

ASSUME = True

from dtaf_core.lib.private.provider_config.bios_setupmenu_provider_config import BiosSetupmenuProviderConfig

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
    setupmenu=[
        ET.fromstring(
            """
            <bios_setupmenu>
                    <driver>
                        <com>
                            <baudrate>115200</baudrate>
                            <port>COM100</port>
                            <timeout>5</timeout>
                        </com>
                    </driver>
                    <efishell_entry select_item="Launch EFI Shell">
                        <path>
                            <node>Setup Menu</node>
                            <node>Boot Manager</node>
                        </path>
                    </efishell_entry>
                    <screen width="100" height="31"/>
                    <continue select_item="Continue"/>
                    <reset press_key="\\33R\\33r\\33R" parse="False"/>
                </bios_setupmenu>
            """
        ),
        OrderedDict([('bios_setupmenu',
                      OrderedDict([
                          ('driver', OrderedDict([
                              ('com', OrderedDict([
                                  ('baudrate', '115200'), ('port', 'COM100'), ('timeout', '5')]))])),
                          ('efishell_entry', OrderedDict([('@select_item', 'Launch EFI Shell'),
                                                          ('path',
                                                           OrderedDict([('node', ['Setup Menu', 'Boot Manager'])]))])),
                          ('continue', OrderedDict([('@select_item', 'Continue')])),
                          ('reset', OrderedDict([('@parse', 'False'), ('@press_key', '\\33R\\33r\\33R')]))]))])
    ]
)


class TestSetupmenuProviderConfig:
    def test_setupmenu_provider_cfg_normal(self):
        for cfg in cfg_dict["setupmenu"]:
            with ProviderCfgFactory.create(cfg, Logs()) as cfg_model:  # type: BiosSetupmenuProviderConfig
                driver_cfg = cfg_model.driver_cfg
                for k, v in cfg_model.__dict__.items():
                    if k != '_BiosSetupmenuProviderConfig__screen':
                        print(k, v)
                        assert v is not None
                for k, v in driver_cfg.__dict__.items():
                    print(k, v)
                    assert v is not None
