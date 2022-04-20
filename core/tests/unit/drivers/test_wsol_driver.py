import xml.etree.ElementTree as ET

from dtaf_core.drivers.internal.wsol_driver import WsolDriver, WebSocketConnection

cfg = ET.fromstring("""
    <wsol>
        <ip>xxx</ip>
        <port>xxx</port>
        <timeout>10</timeout>
        <credentials user="debuguser" password="0penBmc1"/>
    </wsol>
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


def mock_func(*args, **kwargs):
    return


class TestSuites:

    @staticmethod
    def test_write():
        WsolDriver._new_resource = mock_func
        WsolDriver.addr = 'xxx'
        wsol_obj = WsolDriver(cfg, log)

    @staticmethod
    def test_wsol_connect():
        obj = WebSocketConnection(uri='xxx.xxx.xxx.xxx', user='xxx', pw='xxx', log=log)
