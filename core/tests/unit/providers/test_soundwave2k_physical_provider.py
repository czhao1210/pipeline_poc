import six
if six.PY2:
    import mock
if six.PY3 or six.PY34:
    from unittest import mock
import pytest
from dtaf_core.providers.internal.soundwave2k_physical_control_provider import Soundwave2kPhysicalControlProvider
from dtaf_core.lib.exceptions import SoundWaveError
from dtaf_core.drivers.driver_factory import DriverFactory
import time
from dtaf_core.lib.configuration import ConfigurationHelper


class DF:

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def __init__(self, *args, **kwargs):
        pass

    def usb_to_port_a(self):
        return True

    def usb_to_open(self):
        return True

    def usb_to_port_b(self):
        return True

    def ctr_fp_two_ways_switch(self,fp_port, action):
        return True

    def read_s4_pin(self):
        raise NotImplementedError

    def read_s3_pin(self):
        raise NotImplementedError

    def read_postcode(self):
        raise NotImplementedError

    def program_jumper(self):
        raise NotImplementedError

    def close(self):
        pass


class DF_Exception(object):

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def __init__(self, *args, **kwargs):
        pass

    def usb_to_port_a(self):
        raise SoundWaveError

    def usb_to_open(self):
        raise SoundWaveError

    def usb_to_port_b(self):
        raise SoundWaveError

    def ctr_fp_two_ways_switch(self,fp_port, action):
        raise SoundWaveError

    def close(self):
        pass

class _Logs(object):
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


def usb_switch_to_sut_timeout():
    time.sleep(10)
    return r'On'

def usb_switch_to_sut_timeout():
    time.sleep(10)
    return r'On'

cfg_opts = None
log=_Logs()

class TestSoundwave2kPhysicalControlProvider(object):

    
    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('timeout, return_state,state',[(5,True,True),(None,True,True)])
    def test_connect_usb_to_sut(driver_cfg, provider, driver,timeout,return_state,state,mocker, monkeypatch):
        with pytest.raises(SoundWaveError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            mocker.patch.object(DriverFactory, 'create', new=DF)
            raise SoundWaveError('if command execution failed in driver')
        mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
        mocker.patch.object(DriverFactory, 'create', new=DF)
        assert Soundwave2kPhysicalControlProvider(cfg_opts, log).connect_usb_to_sut(timeout) is state

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create',return_value=Exception('Exception'))
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config',return_value=None)
    @pytest.mark.parametrize('timeout, return_state,state',[(5,None,Exception)])
    def test_connect_usb_to_sut_exception(driver_cfg, provider,driver,timeout,return_state,state, mocker, monkeypatch):
        with pytest.raises(SoundWaveError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            driver.return_value=DF_Exception()
            Soundwave2kPhysicalControlProvider(cfg_opts, log).connect_usb_to_sut(timeout)
            raise SoundWaveError('switch flash disk to sut error end')        


    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('timeout, return_state,state',[(5,True,True),(None,True,True)])
    def test_connect_usb_to_host(driver_cfg, provider, driver,timeout,return_state,state,mocker, monkeypatch):
        with pytest.raises(SoundWaveError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            mocker.patch.object(DriverFactory, 'create', new=DF)
            raise SoundWaveError('if command execution failed in driver')
        mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
        mocker.patch.object(DriverFactory, 'create', new=DF)
        assert Soundwave2kPhysicalControlProvider(cfg_opts, log).connect_usb_to_host(timeout) is state

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create',return_value=Exception('Exception'))
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config',return_value=None)
    @pytest.mark.parametrize('timeout, return_state,state',[(5,None,Exception)])
    def test_connect_usb_to_host_exception(driver_cfg, provider,driver,timeout,return_state,state, mocker, monkeypatch):
        with pytest.raises(SoundWaveError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            driver.return_value=DF_Exception()
            Soundwave2kPhysicalControlProvider(cfg_opts, log).connect_usb_to_host(timeout)
            raise SoundWaveError('switch flash disk to host error end')
    

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('timeout, return_state,state',[(5,True,True),(None,True,True)])
    def test_disconnect_usb(driver_cfg, provider, driver,timeout,return_state,state,mocker, monkeypatch):
        with pytest.raises(SoundWaveError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            mocker.patch.object(DriverFactory, 'create', new=DF)
            raise SoundWaveError('if command execution failed in driver')
        mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
        mocker.patch.object(DriverFactory, 'create', new=DF)
        assert Soundwave2kPhysicalControlProvider(cfg_opts, log).disconnect_usb(timeout) is state

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create',return_value=Exception('Exception'))
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config',return_value=None)
    @pytest.mark.parametrize('timeout, return_state,state',[(5,None,Exception)])
    def test_disconnect_usb_exception(driver_cfg, provider,driver,timeout,return_state,state, mocker, monkeypatch):
        with pytest.raises(SoundWaveError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            driver.return_value=DF_Exception()
            Soundwave2kPhysicalControlProvider(cfg_opts, log).disconnect_usb(timeout)
            raise SoundWaveError('switch flash disk to host error end')

    
    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('timeout,fp_port, return_value_state, state',[(5,2,True, True),(5,None,True,True),(None,None,True,True)])
    def test_set_clear_cmos(driver_cfg, provider, driver,timeout,fp_port, return_value_state, state,mocker, monkeypatch):
        with pytest.raises(SoundWaveError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            mocker.patch.object(DriverFactory, 'create', new=DF)
            raise SoundWaveError('if command execution failed in driver')
        mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
        mocker.patch.object(DriverFactory, 'create', new=DF)
        assert Soundwave2kPhysicalControlProvider(cfg_opts, log).set_clear_cmos(timeout,fp_port) is state
    

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create',return_value=Exception('Exception'))
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config',return_value=None)
    @pytest.mark.parametrize('timeout, fp_port,return_state,state',[(5,2,None,Exception)])
    def test_set_clear_cmos_exception(driver_cfg, provider,driver,timeout,fp_port,return_state,state, mocker, monkeypatch):
        with pytest.raises(SoundWaveError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            driver.return_value=DF_Exception()
            Soundwave2kPhysicalControlProvider(cfg_opts, log).set_clear_cmos(timeout,fp_port)
            raise SoundWaveError('cmos_clear error end')
    


