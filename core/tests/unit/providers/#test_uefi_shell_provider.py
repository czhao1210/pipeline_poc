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

from dtaf_core.lib.exceptions import InvalidParameterError, TimeoutException
from dtaf_core.providers.internal.com_uefi_shell_provider import ComUefiShellProvider
from dtaf_core.providers.internal.sol_uefi_shell_provider import SolUefiShellProvider
from dtaf_core.providers.internal.base_uefi_shell_provider import BaseUefiShellProvider


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
    @staticmethod
    def register(buffer_name='', size=4096):
        pass

    @staticmethod
    def read_from(buffer_name=''):
        return ''

    @staticmethod
    def write(data):
        pass


cfg_opts = None
log = _Log()


class TestUefiInit(object):
    @staticmethod
    @pytest.fixture(scope='class', params=['', None, 'others'])
    def invalid_drvname(request):
        return request.param

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    def test_init_com(driver_cfg, provider, driver):
        driver_cfg.return_value = None
        provider.return_value.driver_cfg.name = 'com'
        driver.return_value = _Serial()
        return ComUefiShellProvider(cfg_opts, log)

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    def test_init_sol(driver_cfg, provider, driver):
        driver_cfg.return_value = None
        provider.return_value.driver_cfg.name = 'sol'
        driver.return_value = _Serial()
        return SolUefiShellProvider(cfg_opts, log)

    @staticmethod
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    def test_init_invalid_input(provider, invalid_drvname):
        provider.return_value.driver_cfg.name = invalid_drvname
        with pytest.raises(InvalidParameterError):
            return BaseUefiShellProvider(cfg_opts, log)


class TestUefiFunc(object):
    @staticmethod
    @pytest.fixture(scope='class', params=['com', 'sol'])
    def uefi_obj(request):
        if request.param == 'com':
            return TestUefiInit.test_init_com()
        else:
            return TestUefiInit.test_init_sol()

    @staticmethod
    @pytest.fixture(scope='class', params=['UEFI Interactive Shell', 'EFI Shell version', 'Shell>'])
    def uefi_page(request):
        return request.param

    @staticmethod
    @pytest.fixture(scope='class', params=['', None, 12345])
    def invalid_uefi_cmd(request):
        return request

    @staticmethod
    def test_wait_for_uefi_invalid_timeout(uefi_obj):
        pytest.raises(InvalidParameterError,
                      uefi_obj.wait_for_uefi, timeout=-1)

    @staticmethod
    def test_wait_for_uefi_timeout(uefi_obj):
        pytest.raises(TimeoutException,
                      uefi_obj.wait_for_uefi, timeout=3)

    @staticmethod
    @mock.patch('test_uefi_shell_provider._Serial.read_from')
    def test_wait_for_uefi(read_from, uefi_obj, uefi_page):
        read_from.return_value = uefi_page
        uefi_obj.wait_for_uefi(3)

    @staticmethod
    @mock.patch('test_uefi_shell_provider._Serial.read_from')
    def test_in_uefi_false(read_from, uefi_obj):
        read_from.return_value = ''
        assert uefi_obj.in_uefi() is False

    @staticmethod
    @mock.patch('test_uefi_shell_provider._Serial.read_from')
    def test_in_uefi(read_from, uefi_obj):
        read_from.return_value = 'Shell>'
        assert uefi_obj.in_uefi() is True

    @staticmethod
    def test_exit_uefi(uefi_obj):
        uefi_obj.exit_uefi()

    @staticmethod
    def test_shutdown(uefi_obj):
        uefi_obj.shutdown()

    @staticmethod
    def test_reboot(uefi_obj):
        uefi_obj.reboot()

    @staticmethod
    def test_warm_reset(uefi_obj):
        uefi_obj.warm_reset()

    @staticmethod
    def test_cold_reset(uefi_obj):
        uefi_obj.cold_reset()

    @staticmethod
    def test_execute_invalid_cmd(uefi_obj, invalid_uefi_cmd):
        pytest.raises(InvalidParameterError,
                      uefi_obj.execute, cmd=invalid_uefi_cmd, timeout=3)

    @staticmethod
    def test_execute_invalid_timeout(uefi_obj):
        pytest.raises(InvalidParameterError,
                      uefi_obj.execute, cmd='map -r', timeout=-1)

    @staticmethod
    @mock.patch('test_uefi_shell_provider._Serial.read_from')
    def test_execute_timeout(read_from, uefi_obj):
        read_from.return_value = 'output serial data ...'
        pytest.raises(TimeoutException,
                      uefi_obj.execute, cmd='map -r', timeout=3)

    @staticmethod
    def test_execute_without_output(uefi_obj):
        assert uefi_obj.execute(cmd='reset', timeout=0) == ''

    @staticmethod
    @mock.patch('test_uefi_shell_provider._Serial.read_from')
    def test_execute_with_output(read_from, uefi_obj):
        read_from.return_value = 'fs0:\nfs1: device descriptions \nShell> '
        assert 'fs0:' in uefi_obj.execute(cmd='map -r', timeout=3)

    @staticmethod
    def test_context_scenarios():
        with TestUefiInit.test_init_com() as uefi_obj:
            assert uefi_obj.execute(cmd='reset', timeout=0) == ''


if __name__ == '__main__':
    pytest.main(['-s', '-v', 'test_uefi_shell_provider.py'])
