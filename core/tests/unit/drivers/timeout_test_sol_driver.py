#!/usr/bin/env python

"""
Python Env: Py2.7 & Py3.8
"""

import os
import sys
import pytest
import mock

cwd = os.path.dirname(__file__)
sys.path.append(cwd)
dtaf_dir = os.path.join(cwd, os.pardir, os.pardir, os.pardir, 'src')
if dtaf_dir not in sys.path:
    sys.path.append(dtaf_dir)

from xml.etree import ElementTree as ET

from dtaf_core.lib.exceptions import DriverIOError
from dtaf_core.drivers.internal.sol_driver import SolDriver
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


class _SSH(object):
    class _SHELL(object):
        def __init__(self):
            pass

        def recv(self, size):
            return 'abcdefg'

        def recv_ready(self):
            pass

        def sendall(self, data):
            pass

        def close(self):
            pass

    def __init__(self, cfg_opts):
        self.cfg_opts = cfg_opts

    def set_missing_host_key_policy(self, *args, **kwargs):
        pass

    def connect(self, *args, **kwargs):
        pass

    def invoke_shell(self):
        return self._SHELL()

    def close(self):
        pass


log = _Log()

sol50_new = """<sol>
    <address>10.239.220.50</address>
    <port>2200</port>
    <timeout>120</timeout>
    <credentials user="root" password="123456789"/>
</sol>
"""
sol50_cpy = """<sol>
    <address>10.239.220.50</address>
    <port>2200</port>
    <timeout>120</timeout>
    <credentials user="root" password="123456789"/>
</sol>
"""
sol60_new = """<sol>
    <address>10.239.220.60</address>
    <port>2200</port>
    <timeout>120</timeout>
    <credentials user="root" password="123456789"/>
</sol>
"""

cfg_sol50_new = ET.fromstring(sol50_new)
cfg_sol50_cpy = ET.fromstring(sol50_cpy)
cfg_sol60_new = ET.fromstring(sol60_new)


class TestSolDriver(object):
    @staticmethod
    @pytest.fixture(scope='class', params=[log, None])
    def log_param(request):
        return request.param

    @staticmethod
    @pytest.fixture(scope='class', params=['abcdefghijk', 123, '', None])
    def data_input(request):
        return request.param

    @staticmethod
    @mock.patch('paramiko.SSHClient')
    def test_singleton(ssh):
        ssh.return_value = _SSH(cfg_sol50_new)
        sol50_new = SolDriver(cfg_sol50_new, log)
        ssh.return_value = _SSH(cfg_sol50_cpy)
        sol50_cpy = SolDriver(cfg_sol50_cpy, log)
        ssh.return_value = _SSH(cfg_sol60_new)
        sol60_new = SolDriver(cfg_sol60_new, log)
        assert id(sol50_new) == id(sol50_cpy)
        assert id(sol50_new) != id(sol60_new)
        sol50_new._release()
        sol50_cpy._release()
        sol60_new._release()

    @staticmethod
    @mock.patch('paramiko.SSHClient')
    def test_init_with_args(ssh):
        ssh.return_value = _SSH(cfg_sol50_new)
        sol50_new = SolDriver(cfg_sol50_new, log)
        sol50_new._release()

    @staticmethod
    @mock.patch('paramiko.SSHClient')
    def test_init_with_kwargs(ssh):
        ssh.return_value = _SSH(cfg_sol50_new)
        sol50_new = SolDriver(cfg_opts=cfg_sol50_new, log=log)
        sol50_new._release()

    @staticmethod
    @mock.patch('paramiko.SSHClient')
    def test_init_with_mix(ssh):
        ssh.return_value = _SSH(cfg_sol50_new)
        sol50_new = SolDriver(cfg_sol50_new, log=log)
        sol50_new._release()

    @staticmethod
    @mock.patch('paramiko.SSHClient')
    def test_release_resource(ssh):
        ssh.return_value = _SSH(cfg_sol50_new)
        sol50_new = SolDriver(cfg_sol50_new, log)
        ssh.return_value = _SSH(cfg_sol60_new)
        sol60_new = SolDriver(cfg_sol60_new, log)
        sol50_new._release()
        sol50_new._release()
        sol60_new._release()
        assert sol50_new._serial is None
        assert sol50_new._sol_ssh is None
        assert sol50_new._stopped is True
        assert sol50_new._closed is True
        assert sol60_new._serial is None
        assert sol60_new._sol_ssh is None
        assert sol60_new._stopped is True
        assert sol60_new._closed is True

    @staticmethod
    @mock.patch('paramiko.SSHClient')
    def test_new_resource(ssh):
        ssh.return_value = _SSH(cfg_sol50_new)
        sol50_new = SolDriver(cfg_opts=cfg_sol50_new, log=log)
        assert sol50_new._serial is not None
        assert sol50_new._sol_ssh is not None
        assert sol50_new._stopped is False
        assert sol50_new._closed is False
        sol50_new._release()

    @staticmethod
    @mock.patch('paramiko.SSHClient')
    def test_push_to_all_buffer(ssh):
        ssh.return_value = _SSH(cfg_sol50_new)
        testing_data = 'abcdefg'
        sol50_new = SolDriver(cfg_opts=cfg_sol50_new, log=log)
        sol50_new.register(buffer_name='_TEST_BUFFER', buffer_size=16)
        sol50_new.register(buffer_name='_TEST_BUFFER2', buffer_size=16)
        sol50_new._push_to_all_buffer(testing_data)
        assert testing_data in sol50_new.read_from('_TEST_BUFFER')
        assert testing_data in sol50_new.read_from('_TEST_BUFFER2')
        sol50_new._release()

    @staticmethod
    @mock.patch('paramiko.SSHClient')
    def test_register(ssh):
        ssh.return_value = _SSH(cfg_sol50_new)
        sol50_new = SolDriver(cfg_opts=cfg_sol50_new, log=log)
        sol50_new.register(buffer_name='_TEST_BUFFER', buffer_size=16)
        assert isinstance(sol50_new._buf_set._buf_set['_TEST_BUFFER'], Buffer)
        sol50_new._release()

    @staticmethod
    @mock.patch('paramiko.SSHClient')
    def test_write(ssh):
        ssh.return_value = _SSH(cfg_sol50_new)
        testing_data = 'abcde'
        sol50_new = SolDriver(cfg_opts=cfg_sol50_new, log=log)
        data_len = sol50_new.write(testing_data)
        assert data_len == len(testing_data)
        sol50_new._release()

    @staticmethod
    @mock.patch('paramiko.SSHClient')
    def test_write_raise(ssh):
        ssh.return_value = _SSH(cfg_sol50_new)
        testing_data = 'abcde'
        sol50_new = SolDriver(cfg_opts=cfg_sol50_new, log=log)
        with pytest.raises(DriverIOError):
            sol50_new._closed = True
            sol50_new.write(testing_data)
        with pytest.raises(DriverIOError):
            sol50_new._release()
            sol50_new.write(testing_data)
        sol50_new._release()

    @staticmethod
    @mock.patch('paramiko.SSHClient')
    def test_close(ssh):
        ssh.return_value = _SSH(cfg_sol50_new)
        sol50_new = SolDriver(cfg_opts=cfg_sol50_new, log=log)
        assert sol50_new._serial is not None
        assert sol50_new._sol_ssh is not None
        assert sol50_new._stopped is False
        assert sol50_new._closed is False
        sol50_new.close()
        assert sol50_new._serial is None
        assert sol50_new._sol_ssh is None
        assert sol50_new._closed is True
        assert sol50_new._stopped is False
        sol50_new._release()

    @staticmethod
    @mock.patch('paramiko.SSHClient')
    def test_reopen(ssh):
        ssh.return_value = _SSH(cfg_sol50_new)
        sol50_new = SolDriver(cfg_opts=cfg_sol50_new, log=log)
        assert sol50_new._serial is not None
        assert sol50_new._sol_ssh is not None
        assert sol50_new._stopped is False
        assert sol50_new._closed is False
        sol50_new.close()
        assert sol50_new._serial is None
        assert sol50_new._sol_ssh is None
        assert sol50_new._closed is True
        assert sol50_new._stopped is False
        sol50_new.reopen()
        assert sol50_new._serial is not None
        assert sol50_new._sol_ssh is not None
        assert sol50_new._stopped is False
        assert sol50_new._closed is False
        sol50_new._release()


if __name__ == '__main__':
    pytest.main(['-s', '-v', 'test_sol_driver.py'])


