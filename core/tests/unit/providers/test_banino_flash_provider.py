from dtaf_core.providers.provider_factory import ProviderFactory
from xml.etree import ElementTree as ET
import mock


class Logs:
    def debug(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass


cfg = ET.fromstring(
    r"""
    <flash>
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
    </flash>
    """
)

update_cfg = ET.fromstring(
    """
    <flash>
        <driver>
            <banino>
                    <banino_dll_path>r"C:\\banino\code\Banino_SXState\\x64\ladybirdxxx.dll"</banino_dll_path>
                    <banino_power_cmd>"C:\\banino\code\Banino_SXState"</banino_power_cmd>
                    <ladybird_driver_serial>152903681</ladybird_driver_serial>
                    <image_path>C:\IFWI_Image\</image_path>
                    <image_name>egs.bin</image_name>
                    <rasp>xxx</rasp>
                </banino>
        </driver>
    </flash>
    """
)

class TestSuites:
    @staticmethod
    @mock.patch("dtaf_core.providers.internal.banino_flash_provider.DriverFactory")
    def test_flash_image(mockobj):
        with ProviderFactory.create(cfg, Logs()) as obj:
            obj.flash_image()

    @staticmethod
    def test_chip_identify():
        with ProviderFactory.create(cfg, Logs()) as obj:
            try:
                obj.chip_identify()
            except NotImplementedError:
                return

    @staticmethod
    def test_write():
        with ProviderFactory.create(cfg, Logs()) as obj:
            try:
                obj.write('a', 'b', 'c')
            except NotImplementedError:
                return

    @staticmethod
    def test_current_bmc_version_check():
        with ProviderFactory.create(cfg, Logs()) as obj:
            try:
                obj.current_bmc_version_check()
            except NotImplementedError:
                return

    @staticmethod
    def test_current_bios_version_check():
        with ProviderFactory.create(cfg, Logs()) as obj:
            try:
                obj.current_bios_version_check()
            except NotImplementedError:
                return

    @staticmethod
    def test_current_cpld_version_check():
        with ProviderFactory.create(cfg, Logs()) as obj:
            try:
                obj.current_cpld_version_check()
            except NotImplementedError:
                return

    @staticmethod
    @mock.patch("dtaf_core.providers.internal.banino_flash_provider.DriverFactory")
    def test_flash_image_bmc(mockobj):
        with ProviderFactory.create(cfg, Logs()) as obj:
            obj.flash_image_bmc()

    @staticmethod
    def test_update():
        with ProviderFactory.create(cfg, Logs()) as obj:
            obj.update_configuration(update_cfg, Logs())
