#!/usr/bin/env python

"""
Python Env: Py2.7 & Py3.8
"""

import os
import sys
import pytest
import six

if six.PY2:
    import mock
if six.PY34 or six.PY3:
    from unittest import mock

import time
import random
import string

cwd = os.path.dirname(__file__)
sys.path.append(cwd)
dtaf_dir = os.path.join(cwd, os.pardir, os.pardir, os.pardir, 'src')
if dtaf_dir not in sys.path:
    sys.path.append(dtaf_dir)

from dtaf_core.lib.exceptions import InvalidParameterError
from dtaf_core.providers.internal.base_console_log_provider import BaseConsoleLogProvider


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
        return ''.join(random.sample(
            string.ascii_letters
            + string.digits
            + string.whitespace
            + string.printable,
            random.randint(10, 30)))

    @staticmethod
    def write(data):
        pass


cfg_opts = None
log = _Log()
log_path = os.path.dirname(sys.argv[0]).replace('/', os.sep)


class TestConsoleLog(object):
    @staticmethod
    @pytest.fixture(scope='class', params=['com', 'sol'])
    def valid_drvname(request):
        return request.param

    @staticmethod
    @pytest.fixture(scope='class', params=['', None, 'others'])
    def invalid_drvname(request):
        return request.param

    @staticmethod
    @pytest.fixture(scope='class', params=['caf', '', None])
    def valid_framework(request):
        return request.param

    @staticmethod
    @pytest.fixture(scope='class', params=['others', 'None', 'no'])
    def invalid_framework(request):
        return request.param

    @staticmethod
    @pytest.fixture(scope='class', params=['', None, '##### TEST START #####', 12345.6789])
    def input_line(request):
        return request.param

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    def test_init(driver_cfg, provider, driver, valid_drvname, valid_framework):
        driver_cfg.return_value = None
        provider.return_value.driver_cfg.name = valid_drvname
        provider.return_value.runwith_framework = valid_framework
        provider.return_value.logpath_local = None
        driver.return_value = _Serial()
        return BaseConsoleLogProvider(cfg_opts, log)

    @staticmethod
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    def test_init_invalid_driver(provider, invalid_drvname):
        provider.return_value.driver_cfg.name = invalid_drvname
        with pytest.raises(InvalidParameterError):
            return BaseConsoleLogProvider(cfg_opts, log)

    @staticmethod
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    def test_init_invalid_framework(driver_cfg, provider, valid_drvname, invalid_framework):
        driver_cfg.return_value = None
        provider.return_value.driver_cfg.name = valid_drvname
        provider.return_value.logpath_local = None
        provider.return_value.runwith_framework = invalid_framework
        with pytest.raises(InvalidParameterError):
            return BaseConsoleLogProvider(cfg_opts, log)

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    def test_log_to_local_default(driver_cfg, provider, driver, valid_drvname, valid_framework):
        driver_cfg.return_value = None
        provider.return_value.driver_cfg.name = valid_drvname
        provider.return_value.runwith_framework = valid_framework
        provider.return_value.logpath_local = None
        driver.return_value = _Serial()
        BaseConsoleLogProvider(cfg_opts, log)
        time.sleep(0.5)

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    def test_log_to_local_config(driver_cfg, provider, driver, valid_drvname, valid_framework):
        driver_cfg.return_value = None
        provider.return_value.driver_cfg.name = valid_drvname
        provider.return_value.runwith_framework = valid_framework
        provider.return_value.logpath_local = os.path.join(log_path, 'local_logs')
        driver.return_value = _Serial()
        BaseConsoleLogProvider(cfg_opts, log)
        time.sleep(0.5)

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    def test_log_to_caf(driver_cfg, provider, driver, valid_drvname):
        driver_cfg.return_value = None
        provider.return_value.driver_cfg.name = valid_drvname
        provider.return_value.runwith_framework = 'caf'
        os.environ['CAF_CASE_LOG_PATH'] = os.path.join(log_path, 'caf_logs')
        provider.return_value.logpath_local = os.path.join(log_path, 'local_logs')
        driver.return_value = _Serial()
        BaseConsoleLogProvider(cfg_opts, log)
        time.sleep(0.5)

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    def test_inject_line(driver_cfg, provider, driver, valid_drvname, valid_framework, input_line):
        driver_cfg.return_value = None
        provider.return_value.driver_cfg.name = valid_drvname
        provider.return_value.runwith_framework = valid_framework
        os.environ['CAF_CASE_LOG_PATH'] = os.path.join(log_path, 'caf_logs')
        provider.return_value.logpath_local = os.path.join(log_path, 'local_logs')
        driver.return_value = _Serial()
        console = BaseConsoleLogProvider(cfg_opts, log)
        console.inject_line(input_line)
        time.sleep(0.5)
        if input_line \
                and os.environ['CAF_CASE_LOG_PATH'] \
                and provider.return_value.runwith_framework == 'caf':
            logfile = os.path.join(os.environ['CAF_CASE_LOG_PATH'],
                                   os.path.splitext(os.path.basename(sys.argv[0]))[0]
                                   + '_console.log')
            assert str(input_line) in str(open(logfile).read())


if __name__ == '__main__':
    pytest.main(['-s', '-v', 'test_console_log_provider.py'])
