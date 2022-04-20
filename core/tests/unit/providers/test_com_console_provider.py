import six

if six.PY2:
    import mock

if six.PY3 or six.PY34:
    from unittest import mock
import pytest
from dtaf_core.drivers.driver_factory import DriverFactory
from dtaf_core.providers.internal.com_console_provider import ComConsoleProvider
from dtaf_core.lib.exceptions import DriverIOError
from dtaf_core.lib.configuration import ConfigurationHelper


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


class _Driver(object):

    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def dc_power_on(self, timeout):
        return True

    def dc_power_off(self, timeout):
        return True

    def get_dc_power_state(self):
        return True

    def dc_power_reset(self):
        return True

    def remove_power(self):
        return True

    def connect_power(self):
        return True


class _Driver_exception(object):

    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def register(self, *args, **kwargs):
        return True

    def start(self):
        return True


cfg_opts = None
log = _Log()


class TestSuites(object):

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    def test_notimplemented(driver_cfg, provider, driver, mocker):
        with pytest.raises(DriverIOError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            mocker.patch.object(DriverFactory, 'create', new=_Driver)
            raise DriverIOError('if command execution failed in driver')
        mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
        mocker.patch.object(DriverFactory, 'create', new=_Driver)
        try:
            obj = ComConsoleProvider(cfg_opts, log)
        except:
            return
