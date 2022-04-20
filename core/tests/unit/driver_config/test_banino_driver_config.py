from collections import OrderedDict

from dtaf_core.lib.private.driver_config.banino_driver_config import BaninoDriverConfig
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
            <banino>
							<banino_dll_path>r"C:\\banino\code\Banino_SXState\\x64\ladybird.dll"</banino_dll_path>
							<banino_power_cmd>"C:\\banino\code\Banino_SXState"</banino_power_cmd>
							<ladybird_driver_serial>152903681</ladybird_driver_serial>
                            <image_path>C:\IFWI_Image\</image_path>
							<image_name>egs.bin</image_name>
							<image_path_bmc>xxx</image_path_bmc>
							<image_name_bmc>xxx</image_name_bmc>
							<rasp>xxx</rasp>
                        </banino>
            """
        ),
        OrderedDict([('banino', OrderedDict(
            [('banino_dll_path', 'r"C:\\banino\\code\\Banino_SXState\\x64\\ladybird.dll"'),
             ('banino_power_cmd', '"C:\\banino\\code\\Banino_SXState"'), ('ladybird_driver_serial', '152903681'),
             ('image_path', 'C:\\IFWI_Image\\'), ('image_name', 'egs.bin'), ('image_path_bmc', 'xxx'),
             ('image_name_bmc', 'xxx'),('rasp', 'xxx')]))])
    ]
)


class TestBaninoDriverConfig:
    def test_banino_cfg_normal(self):
        for cfg in cfg_dict["normal"]:
            with DriverCfgFactory.create(cfg, Logs()) as cfg_model:  # type: BaninoDriverConfig
                assert cfg_model.name
                assert cfg_model.banino_dll_path
                assert cfg_model.banino_power_cmd
                assert cfg_model.ladybird_driver_serial
                assert cfg_model.image_path
                assert cfg_model.image_name
                assert cfg_model.image_path_bmc
                assert cfg_model.image_name_bmc
