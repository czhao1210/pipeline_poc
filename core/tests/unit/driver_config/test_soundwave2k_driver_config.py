from collections import OrderedDict

from dtaf_core.lib.private.drivercfg_factory import DriverCfgFactory
from dtaf_core.lib.private.driver_config.soundwave2k_driver_config import Soundwave2kDriverConfig

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
            <soundwave2k enable_s3_detect="False">
                            <baudrate>115200</baudrate>
                            <serial type="1"></serial>
                            <port>COM101</port>
                            <voltagethreholds>
                                <main_power>
                                    <low>0.8</low>
                                    <high>2.85</high>
                                </main_power>
                                <dsw>
                                    <low>0.8</low>
                                    <high>2.85</high>
                                </dsw>
                                <memory>
                                    <low>0.3</low>
                                    <high>2.2</high>
                                </memory>

                            </voltagethreholds>
                        </soundwave2k>
            """
        ),
        OrderedDict([('soundwave2k', OrderedDict(
            [('@enable_s3_detect', 'False'), ('baudrate', '115200'), ('serial', OrderedDict([('@type', '1')])),
             ('port', 'COM101'), ('voltagethreholds', OrderedDict(
                [('main_power', OrderedDict([('low', '0.8'), ('high', '2.85')])),
                 ('dsw', OrderedDict([('low', '0.8'), ('high', '2.85')])),
                 ('memory', OrderedDict([('low', '0.3'), ('high', '2.2')]))]))]))])
    ]
)


class TestRedfishDriverConfig:
    def test_banino_cfg_normal(self):
        for cfg in cfg_dict["normal"]:
            with DriverCfgFactory.create(cfg, Logs()) as cfg_model:  # type: Soundwave2kDriverConfig
                assert cfg_model.name
                assert cfg_model.serial_type
                assert cfg_model.serial_baudrate
                assert cfg_model.serial_port
                assert cfg_model.low_main_power_voltage
                assert cfg_model.high_main_power_voltage
                assert cfg_model.low_dsw_voltage
                assert cfg_model.high_dsw_voltage
                assert cfg_model.low_memory_voltage
                assert cfg_model.high_memory_voltage
