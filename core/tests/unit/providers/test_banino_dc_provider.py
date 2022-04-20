from dtaf_core.providers.provider_factory import ProviderFactory
from xml.etree import ElementTree as ET
import mock


class Logs:
    def debug(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass


cfg = ET.fromstring(
    """
    <dc>
        <timeout>
            <power_on>5</power_on>
            <power_off>20</power_off>
        </timeout>
       <driver>
           <banino>
                    <banino_dll_path>r"C:\\banino\code\Banino_SXState\\x64\ladybird.dll"</banino_dll_path>
                    <banino_power_cmd>"C:\\banino\code\Banino_SXState"</banino_power_cmd>
                    <ladybird_driver_serial>152903681</ladybird_driver_serial>
                    <image_path>C:\IFWI_Image\</image_path>
                    <image_name>egs.bin</image_name>
                    <rasp>xxx</rasp>
                </banino>
        </driver>
    </dc>
    """
)

update_cfg = {"dc": {"timeout": {"power_on": "5", "power_off": "20"}, "driver": {
    "banino": {"banino_dll_path": "r\"C:\\banino\\code\\Banino_SXState\\x64\\ladybirdxxxx.dll\"",
               "banino_power_cmd": "\"C:\\banino\\code\\Banino_SXState\"", "ladybird_driver_serial": "152903681",
               "image_path": "C:\\IFWI_Image\\", "image_name": "egs.bin", "rasp": "xxx"}}}}


class TestSuites:

    @staticmethod
    @mock.patch("dtaf_core.providers.internal.banino_dc_provider.DriverFactory")
    def test_dc_power_on(mockobj):
        with ProviderFactory.create(cfg, Logs()) as obj:
            obj.dc_power_on()

    @staticmethod
    @mock.patch("dtaf_core.providers.internal.banino_dc_provider.DriverFactory")
    def test_dc_power_off(mockobj):
        with ProviderFactory.create(cfg, Logs()) as obj:
            obj.dc_power_off()

    @staticmethod
    @mock.patch("dtaf_core.providers.internal.banino_dc_provider.DriverFactory")
    def test_get_dc_power_state(mockobj):
        with ProviderFactory.create(cfg, Logs()) as obj:
            obj.get_dc_power_state()

    @staticmethod
    @mock.patch("dtaf_core.providers.internal.banino_dc_provider.DriverFactory")
    def test_dc_power_reset(mockobj):
        with ProviderFactory.create(cfg, Logs()) as obj:
            obj.dc_power_reset()

    @staticmethod
    def test_update():
        with ProviderFactory.create(cfg, Logs()) as obj:
            obj.update_configuration(update_cfg, Logs())
