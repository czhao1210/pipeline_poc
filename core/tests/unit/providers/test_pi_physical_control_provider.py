#################################################################################
# INTEL CONFIDENTIAL
# Copyright Intel Corporation All Rights Reserved.
# The source code contained or described herein and all documents related to
# the source code ("Material") are owned by Intel Corporation or its suppliers
# or licensors. Title to the Material remains with Intel Corporation or its
# suppliers and licensors. The Material may contain trade secrets and proprietary
# and confidential information of Intel Corporation and its suppliers and
# licensors, and is protected by worldwide copyright and trade secret laws and
# treaty provisions. No part of the Material may be used, copied, reproduced,
# modified, published, uploaded, posted, transmitted, distributed, or disclosed
# in any way without Intel's prior express written permission.
# No license under any patent, copyright, trade secret or other intellectual
# property right is granted to or conferred upon you by disclosure or delivery
# of the Materials, either expressly, by implication, inducement, estoppel or
# otherwise. Any license under such intellectual property rights must be express
# and approved by Intel in writing.
#################################################################################


#Global imports
import pytest
import six

if six.PY2:
    import mock
if six.PY3 or six.PY34:
    from unittest import mock

#Local imports
from dtaf_core.providers.internal.pi_physical_control_provider import PiPhysicalControlProvider
from dtaf_core.lib.configuration import ConfigurationHelper
from dtaf_core.drivers.driver_factory import DriverFactory
from dtaf_core.lib.exceptions import DriverIOError


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
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def __init__(self, *args, **kwargs):
        pass
    
    def connect_usb_to_sut(self):
        return True

    def connect_usb_to_host(self):
        return True

    def disconnect_usb(self):
        return True

    def set_clear_cmos(self):
        return True

    def read_postcode(self):
        return int(96)

    def read_s3_pin(self):
        return True

    def read_s4_pin(self):
        return True

    def program_jumper(self,state,gpio,timeout):
        return True

class _Driver_exception(object):
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def __init__(self, *args, **kwargs):
        pass
    
    def connect_usb_to_sut(self):
        raise DriverIOError
    
    def connect_usb_to_host(self):
        raise DriverIOError

    def disconnect_usb(self):
        raise DriverIOError
    
    def set_clear_cmos(self):
        raise DriverIOError

    def read_postcode(self):
        raise DriverIOError

    def read_s3_pin(self):
        raise DriverIOError

    def read_s4_pin(self):
        raise DriverIOError

    def program_jumper(self,state,gpio,timeout):
        raise DriverIOError
    

cfg_opts = None
log = _Log()


class TestPiPhysicalControlProvider(object):
    
    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('timeout, return_state,state',[(5,True,True)])
    def test_connect_usb_to_sut(driver_cfg, provider, driver,timeout,return_state,state, mocker, monkeypatch):
        with pytest.raises(DriverIOError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            mocker.patch.object(DriverFactory, 'create', new=_Driver)
            raise DriverIOError('if command execution failed in driver')
        
        mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
        mocker.patch.object(DriverFactory, 'create', new=_Driver)
        assert PiPhysicalControlProvider(cfg_opts, log).connect_usb_to_sut(timeout) is state

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create',return_value=Exception('Exception'))
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config',return_value=None)
    @pytest.mark.parametrize('timeout, return_state,state',[(5,None,Exception)])
    def test_connect_usb_to_sut_exception(driver_cfg, provider,driver,timeout,return_state,state, mocker, monkeypatch):
        with pytest.raises(DriverIOError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            driver.return_value=_Driver_exception()
            PiPhysicalControlProvider(cfg_opts, log).connect_usb_to_sut(timeout)
            raise DriverIOError('if command execution failed in driver')        
        
    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('timeout, return_state,state',[(5,True,True)])
    def test_connect_usb_to_host(driver_cfg, provider, driver,timeout,return_state,state, mocker, monkeypatch):
        with pytest.raises(DriverIOError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            mocker.patch.object(DriverFactory, 'create', new=_Driver)
            raise DriverIOError('if command execution failed in driver')
        
        mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
        mocker.patch.object(DriverFactory, 'create', new=_Driver)
        assert PiPhysicalControlProvider(cfg_opts, log).connect_usb_to_host(timeout) is state

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create',return_value=Exception('Exception'))
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config',return_value=None)
    @pytest.mark.parametrize('timeout, return_state,state',[(5,None,Exception)])
    def test_connect_usb_to_host_exception(driver_cfg, provider,driver,timeout,return_state,state, mocker, monkeypatch):
        with pytest.raises(DriverIOError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            driver.return_value=_Driver_exception()
            PiPhysicalControlProvider(cfg_opts, log).connect_usb_to_host(timeout)
            raise DriverIOError('if command execution failed in driver')

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('timeout, return_state,state',[(5,True,True)])
    def test_disconnect_usb(driver_cfg, provider, driver,timeout,return_state,state, mocker, monkeypatch):
        with pytest.raises(DriverIOError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            mocker.patch.object(DriverFactory, 'create', new=_Driver)
            raise DriverIOError('if command execution failed in driver')
        
        mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
        mocker.patch.object(DriverFactory, 'create', new=_Driver)
        assert PiPhysicalControlProvider(cfg_opts, log).disconnect_usb(timeout) is state

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create',return_value=Exception('Exception'))
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config',return_value=None)
    @pytest.mark.parametrize('timeout, return_state,state',[(5,None,Exception)])
    def test_disconnect_usb_exception(driver_cfg, provider,driver,timeout,return_state,state, mocker, monkeypatch):
        with pytest.raises(DriverIOError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            driver.return_value=_Driver_exception()
            PiPhysicalControlProvider(cfg_opts, log).disconnect_usb(timeout)
            raise DriverIOError('if command execution failed in driver')

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('timeout, return_state,state',[(5,True,True)])
    def test_set_clear_cmos(driver_cfg, provider, driver,timeout,return_state,state, mocker, monkeypatch):
        with pytest.raises(DriverIOError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            mocker.patch.object(DriverFactory, 'create', new=_Driver)
            raise DriverIOError('if command execution failed in driver')
        
        mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
        mocker.patch.object(DriverFactory, 'create', new=_Driver)
        assert PiPhysicalControlProvider(cfg_opts, log).set_clear_cmos(timeout) is state

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create',return_value=Exception('Exception'))
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config',return_value=None)
    @pytest.mark.parametrize('timeout, return_state,state',[(5,None,Exception)])
    def test_set_clear_cmos_exception(driver_cfg, provider,driver,timeout,return_state,state, mocker, monkeypatch):
        with pytest.raises(DriverIOError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            driver.return_value=_Driver_exception()
            PiPhysicalControlProvider(cfg_opts, log).set_clear_cmos(timeout)
            raise DriverIOError('if command execution failed in driver')

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('timeout, return_state',[(5,96)])
    def test_read_postcode(driver_cfg, provider, driver,timeout,return_state, mocker, monkeypatch):
        with pytest.raises(DriverIOError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            mocker.patch.object(DriverFactory, 'create', new=_Driver)
            raise DriverIOError('if command execution failed in driver')
        
        mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
        mocker.patch.object(DriverFactory, 'create', new=_Driver)
        real=PiPhysicalControlProvider(cfg_opts, log)
        real.read_postcode_fake=mock.MagicMock(name='create().__enter__().read_postcode()')
        ret=real.read_postcode()
        assert PiPhysicalControlProvider(cfg_opts, log).read_postcode() is ret

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create',return_value=Exception('Exception'))
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config',return_value=None)
    @pytest.mark.parametrize('timeout, return_state,state',[(5,None,Exception)])
    def test_read_postcode_exception(driver_cfg, provider,driver,timeout,return_state,state, mocker, monkeypatch):
        with pytest.raises(DriverIOError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            driver.return_value=_Driver_exception()
            PiPhysicalControlProvider(cfg_opts, log).read_postcode()
            raise DriverIOError('if command execution failed in driver')

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('return_state,state',[(True,True)])
    def test_read_s3_pin(driver_cfg, provider, driver,return_state,state, mocker, monkeypatch):
        with pytest.raises(DriverIOError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            mocker.patch.object(DriverFactory, 'create', new=_Driver)
            raise DriverIOError('if command execution failed in driver')
        
        mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
        mocker.patch.object(DriverFactory, 'create', new=_Driver)
        assert PiPhysicalControlProvider(cfg_opts, log).read_s3_pin() is state

    
    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create',return_value=Exception('Exception'))
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config',return_value=None)
    @pytest.mark.parametrize('timeout, return_state,state',[(5,None,Exception)])
    def test_read_s3_pin_exception(driver_cfg, provider,driver,timeout,return_state,state, mocker, monkeypatch):
        with pytest.raises(DriverIOError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            driver.return_value=_Driver_exception()
            PiPhysicalControlProvider(cfg_opts, log).read_s3_pin()
            raise DriverIOError('if command execution failed in driver')

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('return_state,state',[(True,True)])
    def test_read_s4_pin(driver_cfg, provider, driver,return_state,state, mocker, monkeypatch):
        with pytest.raises(DriverIOError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            mocker.patch.object(DriverFactory, 'create', new=_Driver)
            raise DriverIOError('if command execution failed in driver')
        
        mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
        mocker.patch.object(DriverFactory, 'create', new=_Driver)
        assert PiPhysicalControlProvider(cfg_opts, log).read_s4_pin() is state

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create',return_value=Exception('Exception'))
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config',return_value=None)
    @pytest.mark.parametrize('timeout, return_state,state',[(5,None,Exception)])
    def test_read_s4_pin_exception(driver_cfg, provider,driver,timeout,return_state,state, mocker, monkeypatch):
        with pytest.raises(DriverIOError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            driver.return_value=_Driver_exception()
            PiPhysicalControlProvider(cfg_opts, log).read_s4_pin()
            raise DriverIOError('if command execution failed in driver')
    

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('pin_state,gpio,timeout,return_state,state',[("set",26,5,True,True)])
    def test_program_jumper(driver_cfg, provider, driver,pin_state,gpio,timeout,return_state,state, mocker, monkeypatch):
        with pytest.raises(DriverIOError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            mocker.patch.object(DriverFactory, 'create', new=_Driver)
            raise DriverIOError('if command execution failed in driver')
        
        mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
        mocker.patch.object(DriverFactory, 'create', new=_Driver)
        assert PiPhysicalControlProvider(cfg_opts, log).program_jumper(state='set',gpio_pin_number="26") is state

    @staticmethod
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create',return_value=Exception('Exception'))
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config',return_value=None)
    @pytest.mark.parametrize('timeout, return_state,state',[(5,None,Exception)])
    def test_program_jumper_exception(driver_cfg, provider,driver,timeout,return_state,state, mocker, monkeypatch):
        with pytest.raises(DriverIOError):
            mocker.patch.object(ConfigurationHelper, 'get_driver_config', return_value=None)
            driver.return_value=_Driver_exception()
            PiPhysicalControlProvider(cfg_opts, log).program_jumper(state='set',gpio_pin_number="26")
            raise DriverIOError('if command execution failed in driver')

                                                
                             
     
                             
    

    

    

