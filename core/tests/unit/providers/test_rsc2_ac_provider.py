import six
if six.PY2:
    import mock

if six.PY3 or six.PY34:
    from unittest import mock

import pytest

from dtaf_core.providers.internal.rsc2_ac_provider import Rsc2AcProvider


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
    def __init__(self, return_state):
        self.return_value = return_state

    def ac_connected(self):
        return self.return_value

    def connect_power(self):
        return self.return_value

    def remove_power(self):
        pass

cfg_opts = None
log = _Log()


class TestRsc2AcProvider(object):
    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('timeout, return_state, state', [(5, True, False),
                                                              (5, False, True),
                                                              ])
    def test_ac_power_off(driver_cfg, provider, driver, timeout, return_state, state):
        driver.return_value = _Driver(return_state)
        assert Rsc2AcProvider(cfg_opts, log).ac_power_off(timeout) is state

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('return_state, state', [(True, True),
                                                     (False, False),
                                                     ])
    def test_get_ac_power_state(driver_cfg, provider,driver, return_state, state):
        driver.return_value = _Driver(return_state)
        assert Rsc2AcProvider(cfg_opts, log).get_ac_power_state() is state

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('timeout, return_state, state', [(5, True, True),
                                                              (5, False, False),
                                                              (None, False, False),
                                                              ])
    def test_ac_power_on(driver_cfg, provider, driver, timeout, return_state, state):
         driver.return_value = _Driver(return_state)
         assert Rsc2AcProvider(cfg_opts, log).ac_power_on(timeout) is state