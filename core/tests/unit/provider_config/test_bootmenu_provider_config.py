from collections import OrderedDict

from dtaf_core.lib.private.providercfg_factory import ProviderCfgFactory

ASSUME = True

from dtaf_core.lib.private.provider_config.bios_bootmenu_provider_config import BiosBootmenuProviderConfig


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
    bootmenu=[
        ET.fromstring(
            """
            <bios_bootmenu>
                    <driver>
                        <com>
                            <baudrate>115200</baudrate>
                            <port>COM100</port>
                            <timeout>5</timeout>
                            
                        </com>
                    </driver>
                    <efishell_entry select_item="Launch EFI Shell"/>
                </bios_bootmenu>
            """
        ),
        OrderedDict([('bios_bootmenu', OrderedDict([('driver', OrderedDict(
            [('com', OrderedDict([('baudrate', '115200'), ('port', 'COM100'), ('timeout', '5')]))])), ('efishell_entry',
                                                                                                       OrderedDict([(
                                                                                                                    '@select_item',
                                                                                                                    'Launch EFI Shell')]))]))])
    ]
)


class TestSetupmenuProviderConfig:
    def test_bootmenu_provider_cfg_normal(self):
        for cfg in cfg_dict["bootmenu"]:
            with ProviderCfgFactory.create(cfg, Logs()) as cfg_model:  # type: BiosBootmenuProviderConfig
                driver_cfg = cfg_model.driver_cfg
                assert cfg_model.driver_cfg
                assert cfg_model.provider_name
                assert cfg_model.efishell_entry
                for k, v in cfg_model.__dict__.items():
                    if k != '_BiosBootmenuProviderConfig__screen':
                        print(k, v)
                        assert v is not None
                for k, v in driver_cfg.__dict__.items():
                    print(k, v)
                    assert v is not None
