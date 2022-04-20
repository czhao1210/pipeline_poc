import xml.etree.ElementTree as ET

cfg = ET.fromstring("""
<ykush>
        <ykusk_app_path>xxx</ykusk_app_path>
</ykush>    
""")


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


log = _Log()


class TestSuites:
    @staticmethod
    def test_init():
        from dtaf_core.drivers.internal.ykush_driver import YkushDriver
        YkushDriver.__init__ = object.__init__
        obj = YkushDriver()
        obj.log = log
        obj.enable_usb_power()
        obj.disable_usb_power()
