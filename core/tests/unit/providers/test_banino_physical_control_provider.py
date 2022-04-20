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
    <physical_control>
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
       <timeout>
            <usbswitch>4</usbswitch>
            <clearcmos>3</clearcmos>>
       </timeout>
    </physical_control>
    """
)

update_cfg = ET.fromstring(
    r"""
        <physical_control>
         <driver>
            <banino>
                <banino_dll_path>r"C:\\banino\code\Banino_SXState\\x64\ladybirdxxxx.dll"</banino_dll_path>
                <banino_power_cmd>"C:\\banino\code\Banino_SXState"</banino_power_cmd>
                <ladybird_driver_serial>152903681</ladybird_driver_serial>
                <image_path>C:\IFWI_Image\</image_path>
                <image_name>egs.bin</image_name>
                <rasp>xxx</rasp>
            </banino>
        </driver>
       <timeout>
            <usbswitch>4</usbswitch>
            <clearcmos>3</clearcmos>>
       </timeout>
    </physical_control>
    """
)

class TestSuites:
    @staticmethod
    @mock.patch("dtaf_core.providers.internal.banino_physical_control_provider.DriverFactory")
    def test_connect_usb_to_sut(mockobj):
        with ProviderFactory.create(cfg, Logs()) as obj:
            obj.connect_usb_to_sut()

    @staticmethod
    @mock.patch("dtaf_core.providers.internal.banino_physical_control_provider.DriverFactory")
    def test_connect_usb_to_host(mockobj):
        with ProviderFactory.create(cfg, Logs()) as obj:
            obj.connect_usb_to_host()

    @staticmethod
    @mock.patch("dtaf_core.providers.internal.banino_physical_control_provider.DriverFactory")
    def test_disconnect_usb(mockobj):
        with ProviderFactory.create(cfg, Logs()) as obj:
            obj.disconnect_usb()

    @staticmethod
    @mock.patch("dtaf_core.providers.internal.banino_physical_control_provider.DriverFactory")
    def test_set_clear_cmos(mockobj):
        with ProviderFactory.create(cfg, Logs()) as obj:
            obj.set_clear_cmos()

    @staticmethod
    def test_read_postcode():
        with ProviderFactory.create(cfg, Logs()) as obj:
            try:
                obj.read_postcode()
            except NotImplementedError:
                return

    @staticmethod
    @mock.patch("dtaf_core.providers.internal.banino_physical_control_provider.DriverFactory")
    def test_read_s3_pin(mockobj):
        with ProviderFactory.create(cfg, Logs()) as obj:
            obj.read_s3_pin()

    @staticmethod
    @mock.patch("dtaf_core.providers.internal.banino_physical_control_provider.DriverFactory")
    def test_read_s4_pin(mockobj):
        with ProviderFactory.create(cfg, Logs()) as obj:
            obj.read_s4_pin()

    @staticmethod
    @mock.patch("dtaf_core.providers.internal.banino_physical_control_provider.DriverFactory")
    def test_get_power_state(mockobj):
        with ProviderFactory.create(cfg, Logs()) as obj:
            obj.get_power_state()

    @staticmethod
    @mock.patch("dtaf_core.providers.internal.banino_physical_control_provider.DriverFactory")
    def test_program_jumper(mockobj):
        with ProviderFactory.create(cfg, Logs()) as obj:
            obj.program_jumper('a', 'b')

    @staticmethod
    def test_get_platform_volt():
        with ProviderFactory.create(cfg, Logs()) as obj:
            try:
                obj.get_platform_volt()
            except NotImplementedError:
                return

    @staticmethod
    def test_enable_usb_ports():
        with ProviderFactory.create(cfg, Logs()) as obj:
            obj.enable_usb_ports()

    @staticmethod
    def test_disable_usb_ports():
        with ProviderFactory.create(cfg, Logs()) as obj:
            obj.disable_usb_ports()

    @staticmethod
    def test_update():
        with ProviderFactory.create(cfg, Logs()) as obj:
            obj.update_configuration(update_cfg, Logs())
