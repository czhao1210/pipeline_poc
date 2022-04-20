from collections import OrderedDict

from dtaf_core.lib.private.driver_config.em100_driver_config import Em100DriverConfig
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
            <em100 type="emulator" cli_path="C:\Program Files (x86)\DediProg\EM100\\">
                <device name="pch" chip="W25Q256FV" usb_ports="1,2" />
                <device name="bmc" chip="W25Q256FV" usb_ports="3,4" />
            </em100>
            """
        ), OrderedDict([('em100', OrderedDict(
            [('@cli_path', 'C:\\Program Files (x86)\\DediProg\\EM100\\'), ('@type', 'emulator'), ('device', [
                OrderedDict([('@chip', 'W25Q256FV'), ('@name', 'pch'), ('@usb_ports', '1,2')]),
                OrderedDict([('@chip', 'W25Q256FV'), ('@name', 'bmc'), ('@usb_ports', '3,4')])])]))])
    ]
)


class TestEm100DriverConfig:
    def test_banino_cfg_normal(self):
        for cfg in cfg_dict["normal"]:
            with DriverCfgFactory.create(cfg, Logs()) as cfg_model:  # type: Em100DriverConfig
                assert cfg_model.name
                assert cfg_model.chip_config
                assert cfg_model.cli_path
