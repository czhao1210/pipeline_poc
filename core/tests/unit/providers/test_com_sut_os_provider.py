from dtaf_core.providers.internal.com_sut_os_provider import ComSutOsProvider
from xml.etree import ElementTree as ET

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

log = _Log()
cfg_opts = ET.fromstring("""
<sut_os name="Linux" subtype="RHEL" version="7.6" kernel="3.10">
                    <shutdown_delay>10</shutdown_delay>
                    <driver>
                        <com>
                            <baudrate>115200</baudrate>
                            <port>COM100</port>
                            <timeout>5</timeout>
                        </com>
                    </driver>
                </sut_os>
""")


class TestComSutOsProvider(object):
    @staticmethod
    def test_com_sut_os_provider():
        with ComSutOsProvider(log=log, cfg_opts=cfg_opts):
            pass