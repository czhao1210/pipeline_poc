from dtaf_core.lib.private.driver_config.raspberrypi_driver_config import RaspberryPiDriverConfig


class mock_text():
    @property
    def text(self):
        return '123'


class MockDict(dict):
    def find(self, *args, **kwargs):
        return mock_text()


cfg = MockDict(key="xxx")


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

    warn = warning
    fatal = critical


class TestSuites:
    @staticmethod
    def test_init():
        obj = RaspberryPiDriverConfig(cfg, _Log())
        assert obj.ac_gpio_phase
        assert obj.ac_gpio_neutral
        assert obj.dc_power_gpio
        assert obj.reboot_gpio
        assert obj.dc_detection_gpio
        assert obj.ac_detection_gpio
        assert obj.clear_cmos_gpio
        assert obj.usb_switch_phase
        try:
            assert obj.usb_switch_datapos
        except AttributeError:
            pass
        assert obj.usb_switch_dataneg
        assert obj.s3_detection_gpio
        assert obj.s4_detection_gpio