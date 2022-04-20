import mock
import pytest
from dtaf_core.drivers.internal.banino_driver import BaninoDriver
import xml.etree.ElementTree as ET


class _Log(object):
    @classmethod
    def debug(cls, msg):
        print(msg)

    @classmethod
    def info(cls, msg):
        print(msg)

    @classmethod
    def warning(cls, msg):
        print(msg)

    @classmethod
    def error(cls, msg):
        print(msg)

    @classmethod
    def critical(cls, msg):
        print(msg)


cfg_normal = ET.fromstring(r"""
                                    <banino>
							<banino_dll_path>r"C:\banino\code\Banino_SXState\x64\ladybird.dll"</banino_dll_path>
							<banino_power_cmd>"C:\banino\code\Banino_SXState"</banino_power_cmd>
							<ladybird_driver_serial>152903681</ladybird_driver_serial>
							<rasp>xxx</rasp>
                            <image_path>C:\IFWI_Image\</image_path>
							<image_name>egs.bin</image_name>
                            <chip_verification_ifwi>no</chip_verification_ifwi>
                            <chip_verification_bmc>yes</chip_verification_bmc>
                        </banino>
        """
                           )


def true_mock(return_value=True, *args, **kwargs):
    return return_value


class TestBaninoDriver(object):

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.banino_driver.ctypes")
    def test_conect_relay(ctypes_mock):
        try:
            ret = BaninoDriver(cfg_normal, log=_Log()).conect_relay('a', 'b')
        except Exception as e:
            print(e)

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.banino_driver.ctypes")
    def test_conect_relay_custom(ctypes_moc):
        try:
            ret = BaninoDriver(cfg_normal, log=_Log()).conect_relay_custom('a')
        except Exception as e:
            print(e)

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.banino_driver.ctypes")
    def test_disconnect_relay_custom(ctypes_mock):
        try:
            ret = BaninoDriver(cfg_normal, log=_Log()).disconnect_relay_custom('a')
        except Exception as e:
            print(e)

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.banino_driver.ctypes")
    def test_disconnect_relay(ctypes_mock):
        try:
            ret = BaninoDriver(cfg_normal, log=_Log()).disconnect_relay('a', 'b')
        except Exception as e:
            print(e)

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.banino_driver.ctypes")
    def test_connect_usb_to_sut(ctypes_mock):
        try:
            ret = BaninoDriver(cfg_normal, log=_Log()).connect_usb_to_sut(5)
        except Exception as e:
            print(e)

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.banino_driver.ctypes")
    def test_connect_usb_to_host(ctypes_mock):
        try:
            ret = BaninoDriver(cfg_normal, log=_Log()).connect_usb_to_host(5)
        except Exception as e:
            print(e)

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.banino_driver.ctypes")
    def test_disconnect_usb(ctypes_mock):
        try:
            ret = BaninoDriver(cfg_normal, log=_Log()).disconnect_usb(5)
        except Exception as e:
            print(e)

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.banino_driver.ctypes")
    def test_set_clear_cmos(ctypes_mock):
        try:
            ret = BaninoDriver(cfg_normal, log=_Log()).set_clear_cmos(5)
        except Exception as e:
            print(e)

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.banino_driver.ctypes")
    def test_dc_power_on(ctypes_mock):
        try:
            ret = BaninoDriver(cfg_normal, log=_Log()).dc_power_on(5)
        except Exception as e:
            print(e)

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.banino_driver.ctypes")
    def test_dc_power_off(ctypes_mock):
        try:
            ret = BaninoDriver(cfg_normal, log=_Log()).dc_power_off(5)
        except Exception as e:
            print(e)

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.banino_driver.ctypes")
    def test_get_dc_power_state(ctypes_mock):
        try:
            ret = BaninoDriver(cfg_normal, log=_Log()).get_dc_power_state()
        except Exception as e:
            print(e)

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.banino_driver.ctypes")
    def test_get_sx_power_state(ctypes_mock):
        try:
            ret = BaninoDriver(cfg_normal, log=_Log()).get_sx_power_state()
        except Exception as e:
            print(e)

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.banino_driver.ctypes")
    def test_dc_power_reset(ctypes_mock):
        try:
            ret = BaninoDriver(cfg_normal, log=_Log()).dc_power_reset()
        except Exception as e:
            print(e)

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.banino_driver.ctypes")
    def test_read_s3_pin(ctypes_mock):
        try:
            ret = BaninoDriver(cfg_normal, log=_Log()).read_s3_pin()
        except Exception as e:
            print(e)

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.banino_driver.ctypes")
    def test_read_s4_pin(ctypes_mock):
        try:
            ret = BaninoDriver(cfg_normal, log=_Log()).read_s4_pin()
        except Exception as e:
            print(e)

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.banino_driver.ctypes")
    def test_get_ac_power_state(ctypes_mock):
        try:
            ret = BaninoDriver(cfg_normal, log=_Log()).get_ac_power_state()
        except Exception as e:
            print(e)

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.banino_driver.ctypes")
    def test_program_jumper(ctypes_mock):
        try:
            ret = BaninoDriver(cfg_normal, log=_Log()).program_jumper('a', 'b', 5)
        except Exception as e:
            print(e)

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.banino_driver.ctypes")
    @pytest.mark.parametrize("FlashReady,FlashErase,FlashWriteFile", [(0, 1, 1), (0, 0, 0), (0, 0, 1), (1, 0, 0)])
    def test_chip_flash(ctypes_mock, FlashReady, FlashErase, FlashWriteFile):
        obj = BaninoDriver(cfg_normal, log=_Log())
        obj.rasp = True
        obj.conect_relay_custom = true_mock
        obj.conect_relay = true_mock
        obj.disconnect_relay_custom = true_mock
        obj.disconnect_relay = true_mock
        obj.ladybird.FlashReady.return_value = FlashReady
        obj.ladybird.FlashErase.return_value = FlashErase
        obj.ladybird.FlashWriteFile.return_value = FlashWriteFile
        obj.chip_flash('a', 'b')

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.banino_driver.ctypes")
    @pytest.mark.parametrize("FlashReady,FlashErase,FlashWriteFile", [(0, 1, 1), (0, 0, 0), (0, 0, 1), (1, 0, 0)])
    def test_chip_flash_bmc(ctypes_mock, FlashReady, FlashErase, FlashWriteFile):
        obj = BaninoDriver(cfg_normal, log=_Log())
        obj.rasp = True
        obj.conect_relay_custom = true_mock
        obj.conect_relay = true_mock
        obj.disconnect_relay_custom = true_mock
        obj.disconnect_relay = true_mock
        obj.ladybird.FlashReady.return_value = FlashReady
        obj.ladybird.FlashErase.return_value = FlashErase
        obj.ladybird.FlashWriteFile.return_value = FlashWriteFile
        obj.chip_flash_bmc('a', 'b')
