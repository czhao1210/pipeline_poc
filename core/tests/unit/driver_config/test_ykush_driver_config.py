import xmltodict

from dtaf_core.lib.private.driver_config.ykush_driver_config import YkushDriverConfig

cfg = xmltodict.parse("""
    <ykush>
        <xxx>xxx</xxx>
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


class TestSuites:
    @staticmethod
    def test_init():
        obj = YkushDriverConfig(cfg, _Log())
        assert obj.ykush_app_path == None

