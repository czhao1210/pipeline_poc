#!/usr/bin/env python

import os
import sys
from dtaf_core.providers.internal.base_console_provider import BaseConsoleProvider
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
    <console>
        <driver>
            <com>
                <baudrate>1</baudrate>
                <port>COM9999</port>
                <timeout>10</timeout>
            </com>
        </driver>
        <credentials user="xxx" password="xxx"/>
        <login_time_delay>1</login_time_delay>
    </console>
""")
log = _Log()
log_path = os.path.dirname(sys.argv[0]).replace('/', os.sep)


class Mock_Serial():
    def __init__(self, *args, **kwargs):
        return

    def register(self, *args, **kwargs):
        return True

    def read_from(self, *args, **kwargs):
        return 'a'

    def write(self, *args, **kwargs):
        return True


def Mock_Execute(*args, **kwargs):
    return True


class TestConsoleLog(object):

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.base_console_provider.DriverFactory')
    def test_wait_for_login(driverfactory_mock):
        driverfactory_mock.create.return_value = Mock_Serial()
        with BaseConsoleProvider(cfg_opts=cfg_opts, log=log) as obj:
            obj.wait_for_login(2)

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.base_console_provider.DriverFactory')
    def test_login(driverfactory_mock):
        driverfactory_mock.create.return_value = Mock_Serial()
        with BaseConsoleProvider(cfg_opts=cfg_opts, log=log) as obj:
            obj.execute = Mock_Execute
            obj.login()

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.base_console_provider.DriverFactory')
    def test_exit(driverfactory_mock):
        driverfactory_mock.create.return_value = Mock_Serial()
        with BaseConsoleProvider(cfg_opts=cfg_opts, log=log) as obj:
            obj.execute = Mock_Execute
            obj.exit()

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.base_console_provider.DriverFactory')
    def test_reboot(driverfactory_mock):
        driverfactory_mock.create.return_value = Mock_Serial()
        with BaseConsoleProvider(cfg_opts=cfg_opts, log=log) as obj:
            obj.execute = Mock_Execute
            obj.reboot()

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.base_console_provider.DriverFactory')
    def test_reboot(driverfactory_mock):
        driverfactory_mock.create.return_value = Mock_Serial()
        with BaseConsoleProvider(cfg_opts=cfg_opts, log=log) as obj:
            obj.execute('aaa', 0, None)
            obj.execute('aaa', 0, 'a')

