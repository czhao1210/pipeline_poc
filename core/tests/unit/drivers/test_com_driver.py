#!/usr/bin/env python

"""
Python Env: Py2.7 & Py3.8
"""

import os
import sys

import mock
import pytest

cwd = os.path.dirname(__file__)
sys.path.append(cwd)
dtaf_dir = os.path.join(cwd, os.pardir, os.pardir, os.pardir, 'src')
if dtaf_dir not in sys.path:
    sys.path.append(dtaf_dir)

from xml.etree import ElementTree as ET

from dtaf_core.lib.exceptions import DriverIOError
from dtaf_core.drivers.internal.com_driver import ComDriver
from serial import SerialException as SerException
from dtaf_core.drivers.internal.base_serial import Buffer


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


class _Serial(object):
    def __init__(self, cfg_opts):
        self.cfg_opts = cfg_opts
        self.open()

    def read(self, size):
        return 'abcdefg'

    def write(self, data):
        return len(data)

    @property
    def in_waiting(self):
        return 1

    def open(self):
        self.is_open = True

    def close(self):
        if self.is_open:
            self.is_open = False


log = _Log()

com100_None = """<com>
    <port></port>
    <baudrate>115200</baudrate>
    <timeout>5</timeout>
</com>
"""

com100_new = """<com>
    <port>COM100</port>
    <baudrate>115200</baudrate>
    <timeout>5</timeout>
</com>
"""
com100_cpy = """<com>
    <port>COM100</port>
    <baudrate>115200</baudrate>
    <timeout>5</timeout>
</com>
"""
com101_new = """<com>
    <port>COM101</port>
    <baudrate>115200</baudrate>
    <timeout>5</timeout>
</com>
"""
cfg_com100_port_None = ET.fromstring(com100_None)
cfg_com100_new = ET.fromstring(com100_new)
cfg_com100_cpy = ET.fromstring(com100_cpy)
cfg_com101_new = ET.fromstring(com101_new)
import serial


def test():
    serial.SerialException("UT")


class TestComDriver:
    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.com_driver.serial.Serial')
    def test_singleton(serial):
        serial.return_value = _Serial(cfg_com100_new)
        com100_new = ComDriver(cfg_com100_new, log)
        serial.return_value = _Serial(cfg_com100_cpy)
        com100_cpy = ComDriver(cfg_com100_cpy, log)
        serial.return_value = _Serial(cfg_com101_new)
        com101_new = ComDriver(cfg_com101_new, log)
        assert id(com100_new) == id(com100_cpy)
        assert id(com100_new) != id(com101_new)
        com100_new._release()
        com100_cpy._release()
        com101_new._release()

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.com_driver.serial.Serial')
    def test_init_with_args(serial):
        serial.return_value = _Serial(cfg_com100_new)
        com100_new = ComDriver(cfg_com100_new, log)
        com100_new._release()

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.com_driver.serial.Serial')
    def test_with_exception(serMock):
        serMock.side_effect = SerException("UT")
        try:
            com100_new = ComDriver(cfg_com100_new, log)
        except Exception:
            pass


    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.com_driver.serial.Serial')
    def test_init_with_kwargs(serial):
        serial.return_value = _Serial(cfg_com100_new)
        com100_new = ComDriver(cfg_opts=cfg_com100_new, log=log)
        try:
            com100_new._release()
        except RuntimeError:
            return

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.com_driver.serial.Serial')
    def test_init_with_mix(serial):
        serial.return_value = _Serial(cfg_com100_new)
        com100_new = ComDriver(cfg_com100_new, log=log)
        com100_new._release()

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.com_driver.serial.Serial')
    def test_release_resource(serial):
        serial.return_value = _Serial(cfg_com100_new)
        com100_new = ComDriver(cfg_com100_new, log)
        serial.return_value = _Serial(cfg_com101_new)
        com101_new = ComDriver(cfg_com101_new, log)
        com100_new._release()
        com100_new._release()
        com101_new._release()
        assert com100_new._serial is None
        assert com100_new._stopped is True
        assert com101_new._serial is None
        assert com101_new._stopped is True
        assert com101_new._closed is True

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.com_driver.serial.Serial')
    def test_new_resource(serial):
        serial.return_value = _Serial(cfg_com100_new)
        com100_new = ComDriver(cfg_opts=cfg_com100_new, log=log)
        assert com100_new._closed is False
        com100_new._release()

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.com_driver.serial.Serial')
    def test_push_to_all_buffer(serial):
        serial.return_value = _Serial(cfg_com100_new)
        testing_data = 'abcdefg'
        com100_new = ComDriver(cfg_opts=cfg_com100_new, log=log)
        com100_new.register(buffer_name='_TEST_BUFFER', buffer_size=16)
        com100_new.register(buffer_name='_TEST_BUFFER2', buffer_size=16)
        com100_new._push_to_all_buffer(testing_data)
        assert testing_data in com100_new.read_from('_TEST_BUFFER')
        assert testing_data in com100_new.read_from('_TEST_BUFFER2')
        com100_new._release()

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.com_driver.serial.Serial')
    def test_register(serial):
        serial.return_value = _Serial(cfg_com100_new)
        com100_new = ComDriver(cfg_opts=cfg_com100_new, log=log)
        com100_new.register(buffer_name='_TEST_BUFFER', buffer_size=16)
        assert isinstance(com100_new._buf_set._buf_set['_TEST_BUFFER'], Buffer)
        com100_new._release()

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.com_driver.serial.Serial')
    def test_write(serial):
        serial.return_value = _Serial(cfg_com100_new)
        testing_data = 'abcde'
        com100_new = ComDriver(cfg_opts=cfg_com100_new, log=log)
        try:
            data_len = com100_new.write(testing_data)
            assert data_len == len(testing_data)
        except DriverIOError:
            pass
        com100_new._release()

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.com_driver.serial.Serial')
    def test_write_raise(serial):
        serial.return_value = _Serial(cfg_com100_new)
        testing_data = 'abcde'
        com100_new = ComDriver(cfg_opts=cfg_com100_new, log=log)
        with pytest.raises(DriverIOError):
            com100_new._closed = True
            com100_new.write(testing_data)

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.com_driver.serial.Serial')
    def test_close(serial):
        serial.return_value = _Serial(cfg_com100_new)
        com100_new = ComDriver(cfg_opts=cfg_com100_new, log=log)
        com100_new.close()
        assert com100_new._serial is None
        assert com100_new._closed is True
        assert com100_new._stopped is True
        com100_new._release()

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.com_driver.serial.Serial')
    def test_reopen(serial):
        serial.return_value = _Serial(cfg_com100_new)
        com100_new = ComDriver(cfg_opts=cfg_com100_new, log=log)
        com100_new.close()
        assert com100_new._serial is None
        assert com100_new._closed is True
        assert com100_new._stopped is True
        com100_new.reopen()
        assert com100_new._serial is None
        assert com100_new._stopped is True
        assert com100_new._closed is True
        com100_new._release()


if __name__ == '__main__':
    pytest.main(['-s', '-v', 'test_com_driver.py'])
