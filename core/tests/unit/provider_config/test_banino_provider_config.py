from collections import OrderedDict

from dtaf_core.lib.private.providercfg_factory import ProviderCfgFactory

ASSUME = True

from dtaf_core.lib.private.provider_config.banino_provider_config import BaninoProviderConfig

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


cfg = ET.fromstring("""
                <banino>
                    <banino_dll_path>r"C:\\banino\code\Banino_SXState\\x64\ladybird.dll"</banino_dll_path>
                    <banino_power_cmd>"C:\\banino\code\Banino_SXState"</banino_power_cmd>
                    <ladybird_driver_serial>152903681</ladybird_driver_serial>
                    <image_path>C:\IFWI_Image\</image_path>
                    <image_name>egs.bin</image_name>
                    <image_path_bmc>xxx</image_path_bmc>
                    <image_name_bmc>xxx</image_name_bmc>
                    <rasp>xxx</rasp>
                    <driver>
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
                    </driver>
                </banino>
""")


class TestSuites:
    def test_cfg_normal(self):
        with ProviderCfgFactory.create(cfg, Logs()) as cfg_model:  # type: BaninoProviderConfig
            assert cfg_model.provider_name
            assert cfg_model.banino_dll_path
            assert cfg_model.banino_power_cmd
            assert cfg_model.ladybird_driver_serial
            assert cfg_model.image_path
            assert cfg_model.image_name
            assert cfg_model.image_path_bmc
            assert cfg_model.image_name_bmc
