import six

if six.PY2:
    import mock

if six.PY3 or six.PY34:
    from unittest import mock
import pytest
from dtaf_core.providers.internal.pdupi_ac_provider import PdupiAcProvider
from dtaf_core.lib.exceptions import DriverIOError
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.drivers.driver_factory import DriverFactory


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

    def ac_power_on(self, username, password, channel, timeout):
        return True

    def ac_power_off(self, username, password, channel, timeout):
        return True

    def get_ac_power_state(self, username, password, channel):
        return True

    def set_username_password(self, username, password, channel):
        return True

    def reset_username_password(self, channel, masterkey):
        return True


class _Driver_exception(object):

    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def ac_power_on(self, username, password, channel, timeout):
        raise DriverIOError

    def ac_power_off(self, username, password, channel, timeout):
        raise DriverIOError

    def get_ac_power_state(self, username, password, channel):
        raise DriverIOError

    def set_username_password(self, username, password, channel):
        raise DriverIOError

    def reset_username_password(self, channel, masterkey):
        raise DriverIOError


cfg_opts = None
log = _Log()


class TestPduPdupiAcProvider(object):

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('username,password,channel,timeout, return_state, state',
                             [('root', 'pass', 'channel', 5, True, True),
                              ('root1', 'pass1', 'channel1', 5, False, True),
                              ('root2', 'pass2', 'channel2', None, True, True)])
    def test_ac_power_on(driver_cfg, provider, driver, username, password, channel, timeout, return_state, state,
                         mocker, monkeypatch):
        with pytest.raises(DriverIOError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            mocker.patch.object(DriverFactory, 'create', new=_Driver)
            raise DriverIOError('if command execution failed in driver')
        mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
        mocker.patch.object(DriverFactory, 'create', new=_Driver)
        assert PdupiAcProvider(cfg_opts, log).ac_power_on(username, password, channel, timeout) is state

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create',
                return_value=Exception('Exception'))
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config', return_value=None)
    @pytest.mark.parametrize('username,password,channel,timeout, return_state, state',
                             [('root', 'pass', 'channel', 5, None, Exception)])
    def test_ac_power_on_exception(driver_cfg, provider, driver, username, password, channel, timeout, return_state,
                                   state, mocker, monkeypatch):
        with pytest.raises(DriverIOError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            driver.return_value = _Driver_exception()
            PdupiAcProvider(cfg_opts, log).ac_power_on(username, password, channel, timeout)
            raise DriverIOError('pdupi ac power on error')

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('username,password,channel,timeout, return_state, state',
                             [('root', 'pass', 'channel', 5, True, True),
                              ('root1', 'pass1', 'channel1', 5, False, True),
                              ('root2', 'pass2', 'channel2', None, True, True)])
    def test_ac_power_off(driver_cfg, provider, driver, username, password, channel, timeout, return_state, state,
                          mocker, monkeypatch):
        with pytest.raises(DriverIOError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            mocker.patch.object(DriverFactory, 'create', new=_Driver)
            raise DriverIOError('if command execution failed in driver')
        mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
        mocker.patch.object(DriverFactory, 'create', new=_Driver)
        assert PdupiAcProvider(cfg_opts, log).ac_power_off(username, password, channel, timeout) is state

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create',
                return_value=Exception('Exception'))
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config', return_value=None)
    @pytest.mark.parametrize('username,password,channel,timeout, return_state, state',
                             [('root', 'pass', 'channel', 5, None, Exception)])
    def test_ac_power_off_exception(driver_cfg, provider, driver, username, password, channel, timeout, return_state,
                                    state, mocker, monkeypatch):
        with pytest.raises(DriverIOError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            driver.return_value = _Driver_exception()
            PdupiAcProvider(cfg_opts, log).ac_power_off(username, password, channel, timeout)
            raise DriverIOError('pdupi ac power off error')

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('username,password,channel,return_state, state',
                             [('root', 'password', 'channel', True, True),
                              ('root1', 'password1', 'channel1', None, True),
                              ])
    def test_get_ac_power_state(driver_cfg, provider, driver, username, password, channel, return_state, state, mocker,
                                monkeypatch):
        with pytest.raises(DriverIOError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            mocker.patch.object(DriverFactory, 'create', new=_Driver)
            raise DriverIOError('if command execution failed in driver')
        mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
        mocker.patch.object(DriverFactory, 'create', new=_Driver)
        assert PdupiAcProvider(cfg_opts, log).get_ac_power_state(username, password, channel) is state

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create',
                return_value=Exception('Exception'))
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config', return_value=None)
    @pytest.mark.parametrize('username,password,channel, return_state,state',
                             [('root', 'password', 'channel', None, Exception)])
    def test_get_ac_power_state_exception(driver_cfg, provider, driver, username, password, channel, return_state,
                                          state, mocker, monkeypatch):
        with pytest.raises(DriverIOError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            driver.return_value = _Driver_exception()
            PdupiAcProvider(cfg_opts, log).get_ac_power_state(username, password, channel)
            raise DriverIOError('pdupi ac power off error')

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('username,password,channel,return_state, state',
                             [('root', 'password', 'channel', True, True),
                              ('root1', 'password1', 'channel1', None, True),
                              ])
    def test_set_username_password(driver_cfg, provider, driver, username, password, channel, return_state, state,
                                   mocker, monkeypatch):
        with pytest.raises(DriverIOError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            mocker.patch.object(DriverFactory, 'create', new=_Driver)
            raise DriverIOError('if command execution failed in driver')
        mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
        mocker.patch.object(DriverFactory, 'create', new=_Driver)
        assert PdupiAcProvider(cfg_opts, log).set_username_password(username, password, channel) is state

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create',
                return_value=Exception('Exception'))
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config', return_value=None)
    @pytest.mark.parametrize('username,password,channel, return_state,state',
                             [('root', 'password', 'channel', None, Exception)])
    def test_set_username_password_exception(driver_cfg, provider, driver, username, password, channel, return_state,
                                             state, mocker, monkeypatch):
        with pytest.raises(DriverIOError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            driver.return_value = _Driver_exception()
            PdupiAcProvider(cfg_opts, log).set_username_password(username, password, channel)
            raise DriverIOError('pdupi set username password error')

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('channel, masterkey, return_state, state', [('channel', 'masterkey', True, True),
                                                                         ('channel1', 'masterkey1', None, True),
                                                                         ])
    def test_reset_username_password(driver_cfg, provider, driver, channel, masterkey, return_state, state, mocker,
                                     monkeypatch):
        with pytest.raises(DriverIOError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            mocker.patch.object(DriverFactory, 'create', new=_Driver)
            raise DriverIOError('if command execution failed in driver')
        mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
        mocker.patch.object(DriverFactory, 'create', new=_Driver)
        assert PdupiAcProvider(cfg_opts, log).reset_username_password(channel, masterkey) is state

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create',
                return_value=Exception('Exception'))
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config', return_value=None)
    @pytest.mark.parametrize('channel, masterkey, return_state,state', [('channel', 'masterkey', None, Exception)])
    def test_reset_username_password_exception(driver_cfg, provider, driver, channel, masterkey, return_state, state,
                                               mocker, monkeypatch):
        with pytest.raises(DriverIOError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            driver.return_value = _Driver_exception()
            PdupiAcProvider(cfg_opts, log).reset_username_password(channel, masterkey)
            raise DriverIOError('pdupi set username password error')