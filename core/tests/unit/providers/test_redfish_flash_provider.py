#!/usr/bin/env python

import os
import sys
from dtaf_core.providers.internal.redfish_flash_provider import RedfishFlashProvider
from xml.etree import ElementTree as ET
import mock


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


cfg_opts = ET.fromstring("""
    <flash id="1">
        <driver>
            <redfish>
                <ip>xxx</ip>
                <username>xxx</username>
                <password>xxx</password>
                <image_path_bmc>xxx</image_path_bmc>
                <image_name_bmc>xxx</image_name_bmc>
            </redfish>
        </driver>
    </flash>
""")
log = _Log()
log_path = os.path.dirname(sys.argv[0]).replace('/', os.sep)


class Factory_Mock():
    def __init__(self, *args, **kwargs):
        return

    def create(self, *args, **kwargs):
        return Create_Mock()


class Create_Mock():
    def __init__(self, *args, **kwargs):
        return

    def chip_flash_bios(self, *args, **kwargs):
        return True


class TestConsoleLog(object):

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.redfish_flash_provider.DriverFactory')
    def test_flash_image(factory_mock):
        with RedfishFlashProvider(cfg_opts=cfg_opts, log=log) as obj:
            obj.flash_image(target='cpld')

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.redfish_flash_provider.DriverFactory')
    def test_current_bios_version_check(factory_mock):
        with RedfishFlashProvider(cfg_opts=cfg_opts, log=log) as obj:
            obj.current_bios_version_check()

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.redfish_flash_provider.DriverFactory')
    def test_chip_identify(factory_mock):
        with RedfishFlashProvider(cfg_opts=cfg_opts, log=log) as obj:
            try:
                obj.chip_identify()
            except:
                pass

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.redfish_flash_provider.DriverFactory')
    def test_read(factory_mock):
        with RedfishFlashProvider(cfg_opts=cfg_opts, log=log) as obj:
            try:
                obj.read()
            except:
                pass

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.redfish_flash_provider.DriverFactory')
    def test_write(factory_mock):
        with RedfishFlashProvider(cfg_opts=cfg_opts, log=log) as obj:
            try:
                obj.write('a', 'b', 'c')
            except:
                pass

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.redfish_flash_provider.DriverFactory')
    def test_current_bmc_version_check(factory_mock):
        with RedfishFlashProvider(cfg_opts=cfg_opts, log=log) as obj:
                obj.current_bmc_version_check()

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.redfish_flash_provider.DriverFactory')
    def test_flash_image_bmc(factory_mock):
        with RedfishFlashProvider(cfg_opts=cfg_opts, log=log) as obj:
            obj.flash_image_bmc()