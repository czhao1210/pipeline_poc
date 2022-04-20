import xml.etree.ElementTree as ET

import mock

from dtaf_core.providers.internal.base_bios_redfish_provider import BaseBiosRedfishProvider

cfg = ET.fromstring("""
<redfish>
    <driver>
        <com>
            <port>COM21</port>
            <baudrate>115200</baudrate>
            <timeout>5</timeout>
        </com>
    </driver>
    <image_path_bmc>xxx</image_path_bmc>
</redfish>
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
    @mock.patch('dtaf_core.providers.internal.base_bios_redfish_provider.DriverFactory')
    @mock.patch('dtaf_core.providers.internal.base_bios_redfish_provider.ConfigurationHelper')
    def test_init(configurationhelper_mock, drivercfgfactory_mock):
        obj = BaseBiosRedfishProvider(cfg, _Log())
        obj.set_bios_bootorder()
        obj.get_bios_bootorder()
