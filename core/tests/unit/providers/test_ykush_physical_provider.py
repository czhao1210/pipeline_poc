import six

if six.PY2:
    import mock

if six.PY3 or six.PY34:
    from unittest import mock
import pytest
from dtaf_core.drivers.driver_factory import DriverFactory
from dtaf_core.providers.internal.ykush_physical_provider import KushPhysicalControlProvider
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
        obj = KushPhysicalControlProvider(cfg_opts, log)
        try:
            obj.connect_usb_to_sut()
        except NotImplementedError:
            pass

        try:
            obj.connect_usb_to_host()
        except NotImplementedError:
            pass

        try:
            obj.disconnect_usb()
        except NotImplementedError:
            pass

        try:
            obj.set_clear_cmos()
        except NotImplementedError:
            pass

        try:
            obj.read_postcode()
        except NotImplementedError:
            pass

        try:
            obj.read_s3_pin()
        except NotImplementedError:
            pass

        try:
            obj.read_s4_pin()
        except NotImplementedError:
            pass

        try:
            obj.program_jumper('a', 'b')
        except NotImplementedError:
            pass

        try:
            obj.get_power_state()
        except NotImplementedError:
            pass

        try:
            obj.get_platform_volt()
        except NotImplementedError:
            pass

        try:
            obj.enable_usb_ports()
        except AttributeError:
            pass

        try:
            obj.disable_usb_ports()
        except AttributeError:
            pass
