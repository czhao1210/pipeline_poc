#!/usr/bin/env python

"""
Python Env: Py2.7 & Py3.8
"""

import os
import sys
import pytest

cwd = os.path.dirname(__file__)
sys.path.append(cwd)
dtaf_dir = os.path.join(cwd, os.pardir, os.pardir, os.pardir, 'src')
if dtaf_dir not in sys.path:
    sys.path.append(dtaf_dir)

from dtaf_core.lib.exceptions import IncorrectKeyException
from dtaf_core.drivers.internal.base_serial import Buffer, SerialBufferSet


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


cfg_opts = None
log = _Log()

BUFFER_NAME = '_TEST_BUFFER'
BUFFER_SIZE = 16


class TestBuffer(object):
    @staticmethod
    @pytest.fixture(scope='class', params=[log, None])
    def log_param(request):
        return request.param

    @staticmethod
    @pytest.fixture(scope='class', params=['abcdefghijk', 123, '', None])
    def data_input(request):
        return request.param

    @staticmethod
    @pytest.fixture(scope='function')
    def testing_buffer(log_param):
        print('\nINIT BUFFER...')
        buffer = Buffer(name=BUFFER_NAME, max_size=BUFFER_SIZE, log=log_param)
        yield buffer
        print('\nCLEAN BUFFER...')
        buffer.clean()

    @staticmethod
    def test_pull(testing_buffer, data_input):
        testing_buffer.push(data_input)
        assert testing_buffer.pull() == (str(data_input) if data_input else '')

    @staticmethod
    def test_clean(testing_buffer, data_input):
        testing_buffer.push(data_input)
        assert testing_buffer.pull() == (str(data_input) if data_input else '')
        testing_buffer.clean()
        assert testing_buffer.pull() == ''

    @staticmethod
    def test_push_if_less_equal_than_maxsize(testing_buffer, log_param, data_input):
        testing_buffer.push(data_input)
        assert testing_buffer.pull() == (str(data_input) if data_input else '')

    @staticmethod
    def test_push_if_greater_than_maxsize(testing_buffer):
        testing_data = '   abcdefghijklmnopqrstuvwxyz'
        testing_buffer.push(testing_data)
        assert testing_buffer.pull() == testing_data[0:BUFFER_SIZE]


class TestSerialBufferSet(object):
    @staticmethod
    @pytest.fixture(scope='function')
    def buffer_set():
        print('\nINIT BUFFER SET...')
        bset = SerialBufferSet(log)
        yield bset
        print('\nCLEAN BUFFER SET...')
        bset._buf_set = {}

    @staticmethod
    def test_new_buffer(buffer_set):
        buffer = buffer_set.new_buffer(name=BUFFER_NAME, max_size=BUFFER_SIZE)
        assert isinstance(buffer, Buffer)
        assert BUFFER_NAME in buffer_set.buffers_name()
        buffer_set.new_buffer(BUFFER_NAME, BUFFER_SIZE)
        buffer_set.new_buffer(BUFFER_NAME + 'c', BUFFER_SIZE)
        assert len(buffer_set._buf_set) == 2

    @staticmethod
    def test_get_buffer_data(buffer_set):
        testing_data = 'abcdefghijk'
        with pytest.raises(IncorrectKeyException):
            buffer_set.get_buffer_data(BUFFER_NAME)
        buffer = buffer_set.new_buffer(name=BUFFER_NAME, max_size=BUFFER_SIZE)
        buffer_set.push_to_buffer(BUFFER_NAME, testing_data)
        assert buffer_set.get_buffer_data(BUFFER_NAME) == buffer.pull() == testing_data

    @staticmethod
    def test_clean_buffer(buffer_set):
        testing_data = 'abcdefghijk'
        with pytest.raises(IncorrectKeyException):
            buffer_set.clean_buffer(BUFFER_NAME)
        buffer_set.new_buffer(name=BUFFER_NAME, max_size=BUFFER_SIZE)
        buffer_set.push_to_buffer(BUFFER_NAME, testing_data)
        assert buffer_set.get_buffer_data(BUFFER_NAME) == testing_data
        buffer_set.clean_buffer(BUFFER_NAME)
        assert buffer_set.get_buffer_data(BUFFER_NAME) == ''

    @staticmethod
    def test_push_to_buffer(buffer_set):
        testing_data = 'abcdefghijk'
        with pytest.raises(IncorrectKeyException):
            buffer_set.push_to_buffer(BUFFER_NAME, testing_data)
        buffer_set.new_buffer(name=BUFFER_NAME, max_size=BUFFER_SIZE)
        buffer_set.new_buffer(name=BUFFER_NAME + 'c', max_size=BUFFER_SIZE)
        buffer_set.push_to_buffer(BUFFER_NAME, testing_data)
        buffer_set.push_to_buffer(BUFFER_NAME + 'c', testing_data)
        assert buffer_set.get_buffer_data(BUFFER_NAME) \
               == buffer_set.get_buffer_data(BUFFER_NAME + 'c') \
               == testing_data

    @staticmethod
    def test_buffers_name(buffer_set):
        buffer_set.new_buffer(name=BUFFER_NAME, max_size=BUFFER_SIZE)
        buffer_set.new_buffer(name=BUFFER_NAME + 'c', max_size=BUFFER_SIZE)
        assert set(buffer_set.buffers_name()) == {BUFFER_NAME, BUFFER_NAME + 'c'}


if __name__ == '__main__':
    pytest.main(['-s', '-v', 'test_base_serial_driver.py'])
