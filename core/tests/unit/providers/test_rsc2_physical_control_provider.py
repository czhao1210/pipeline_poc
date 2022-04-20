import six
import pytest
if six.PY2:
    import mock

if six.PY3 or six.PY34:
    from unittest import mock
from dtaf_core.providers.internal.rsc2_physical_control_provider import Rsc2PhysicalControlProvider

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

    def connect_usb_to_sut(self):
        return self.return_value

    def connect_usb_to_host(self):
        return self.return_value

    def disconnect_usb(self):
        return self.return_value

    def read_s4_pin(self):
        return self.return_value
    
    

cfg_opts = None
log = _Log()


class TestRsc2PhysicalControlProvider(object):
    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('timeout, return_state,state',[(5,True,True),(None,True,True)])
    def test_connect_usb_to_sut(driver_cfg, provider, driver,timeout,return_state,state):
        driver.return_value = _Driver(return_state)
        assert Rsc2PhysicalControlProvider(cfg_opts, log).connect_usb_to_sut(timeout) is state

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('timeout, return_state,state',[("10",True,True)])
    def test_connect_usb_to_sut_isinstance_error(driver_cfg, provider, driver,timeout,return_state,state):
        driver.return_value = _Driver(return_state)
        with pytest.raises(AttributeError):
            Rsc2PhysicalControlProvider(cfg_opts, log).connect_usb_to_sut(timeout)
    
    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('timeout, return_state,state',[(5,True,True),(None,True,True)])
    def test_connect_usb_to_host(driver_cfg, provider, driver,timeout,return_state,state):
        driver.return_value = _Driver(return_state)
        assert Rsc2PhysicalControlProvider(cfg_opts, log).connect_usb_to_host(timeout) is state

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('timeout, return_state,state',[("10",True,True)])
    def test_connect_usb_to_host_isinstance(driver_cfg, provider, driver,timeout,return_state,state):
        driver.return_value = _Driver(return_state)
        with pytest.raises(AttributeError):
            Rsc2PhysicalControlProvider(cfg_opts, log).connect_usb_to_host(timeout)

    
    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('timeout, return_state,state',[(5,True,True)])
    def test_disconnect_usb(driver_cfg, provider, driver,timeout,return_state,state):
        driver.return_value = _Driver(return_state)
        assert Rsc2PhysicalControlProvider(cfg_opts, log).disconnect_usb(timeout) is state
        
    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('timeout, return_state,state',[(None,True,True)])
    def test_disconnect_usb_isinstance(driver_cfg, provider, driver,timeout,return_state,state):
        driver.return_value = _Driver(return_state)
        with pytest.raises(AttributeError):
            Rsc2PhysicalControlProvider(cfg_opts, log).disconnect_usb(timeout)
    
    '''
    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.rsc2_driver.Rsc2Driver.factory')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('timeout, return_state,state',[(5,True,True)])
    def test_set_clear_cmos(driver_cfg, provider, driver,timeout,return_state,state):
        driver.return_value = _Driver(return_state)
        assert Rsc2PhysicalControlProvider(cfg_opts, log).connect_set_clear_cmos(timeout) is state
    '''
    


    
    
