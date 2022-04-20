import six

if six.PY2:
    import mock

if six.PY3 or six.PY34:
    from unittest import mock
import pytest
from dtaf_core.drivers.driver_factory import DriverFactory
from dtaf_core.providers.internal.redfish_dc_provider import RedfishDcProvider
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


class _Driver_exception(object):

    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def dc_power_on(self, timeout):
        raise DriverIOError

    def dc_power_off(self, timeout):
        raise DriverIOError

    def get_dc_power_state(self):
        raise DriverIOError

    def dc_power_reset(self):
        raise DriverIOError


cfg_opts = None
log = _Log()


class TestRedfishDcProvider(object):

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('timeout, return_state, state',
                             [(5, True, True),
                              (5, False, True),
                              (None, True, True)])
    def test_dc_power_on(driver_cfg, provider, driver, timeout, return_state, state, mocker):
        with pytest.raises(DriverIOError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            mocker.patch.object(DriverFactory, 'create', new=_Driver)
            raise DriverIOError('if command execution failed in driver')
        mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
        mocker.patch.object(DriverFactory, 'create', new=_Driver)
        assert RedfishDcProvider(cfg_opts, log).dc_power_on(timeout) is state

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create',
                return_value=Exception('Exception'))
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config', return_value=None)
    @pytest.mark.parametrize('timeout, return_state, state',
                             [(5, None, Exception)])
    def test_dc_power_on_exception(driver_cfg, provider, driver, timeout, return_state,
                                   state, mocker):
        with pytest.raises(DriverIOError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            driver.return_value = _Driver_exception()
            RedfishDcProvider(cfg_opts, log).dc_power_on(timeout)
            raise DriverIOError('redfish dc power on error')

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('timeout, return_state, state',
                             [(5, True, True),
                              (5, False, True),
                              (None, True, True)])
    def test_dc_power_off(driver_cfg, provider, driver, timeout, return_state, state, mocker):
        with pytest.raises(DriverIOError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            mocker.patch.object(DriverFactory, 'create', new=_Driver)
            raise DriverIOError('if command execution failed in driver')
        mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
        mocker.patch.object(DriverFactory, 'create', new=_Driver)
        assert RedfishDcProvider(cfg_opts, log).dc_power_off(timeout) is state

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create',
                return_value=Exception('Exception'))
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config', return_value=None)
    @pytest.mark.parametrize('timeout, return_state, state',
                             [(5, None, Exception)])
    def test_dc_power_off_exception(driver_cfg, provider, driver, timeout, return_state,
                                    state, mocker):
        with pytest.raises(DriverIOError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            driver.return_value = _Driver_exception()
            RedfishDcProvider(cfg_opts, log).dc_power_off(timeout)
            raise DriverIOError('redfish dc power off error')

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('return_state, state',
                             [(True, True),
                              (False, True),
                              (True, True)])
    def test_get_dc_power_state(driver_cfg, provider, driver, return_state, state, mocker):
        with pytest.raises(DriverIOError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            mocker.patch.object(DriverFactory, 'create', new=_Driver)
            raise DriverIOError('if command execution failed in driver')
        mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
        mocker.patch.object(DriverFactory, 'create', new=_Driver)
        assert RedfishDcProvider(cfg_opts, log).get_dc_power_state() is state

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create',
                return_value=Exception('Exception'))
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config', return_value=None)
    @pytest.mark.parametrize('return_state, state',
                             [(None, Exception)])
    def test_get_dc_power_state_exception(driver_cfg, provider, driver, return_state,
                                          state, mocker):
        with pytest.raises(DriverIOError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            driver.return_value = _Driver_exception()
            RedfishDcProvider(cfg_opts, log).get_dc_power_state()
            raise DriverIOError('redfish dc get power state error')

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('return_state, state',
                             [(True, True),
                              (False, True),
                              (True, True)])
    def test_dc_power_reset(driver_cfg, provider, driver, return_state, state, mocker):
        with pytest.raises(DriverIOError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            mocker.patch.object(DriverFactory, 'create', new=_Driver)
            raise DriverIOError('if command execution failed in driver')
        mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
        mocker.patch.object(DriverFactory, 'create', new=_Driver)
        assert RedfishDcProvider(cfg_opts, log).dc_power_reset() is state

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create',
                return_value=Exception('Exception'))
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config', return_value=None)
    @pytest.mark.parametrize('return_state, state',
                             [(None, Exception)])
    def test_dc_power_reset_exception(driver_cfg, provider, driver, return_state,
                                      state, mocker):
        with pytest.raises(DriverIOError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            driver.return_value = _Driver_exception()
            RedfishDcProvider(cfg_opts, log).dc_power_reset()
            raise DriverIOError('redfish dc get power state error')
