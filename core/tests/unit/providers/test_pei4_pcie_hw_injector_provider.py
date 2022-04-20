import six

if six.PY2:
    import mock

if six.PY3 or six.PY34:
    from unittest import mock
from dtaf_core.providers.internal.pei4_pcie_hw_injector_provider import Pei4PcieHwInjectorProvider
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
        obj = Pei4PcieHwInjectorProvider(cfg_opts, log)
        obj._pei = mock.Mock()
        reg_mock = mock.Mock()
        obj._pei.port = [reg_mock, reg_mock, reg_mock]
        obj.switch_mode(1)
        try:
            obj.open_session()
        except NotImplementedError:
            pass
        try:
            obj.close_session()
        except NotImplementedError:
            pass
        obj.check_link_speed()
        obj.inject_bad_lcrc_err()
        obj.inject_bad_tlp_err()
        obj.inject_bad_dllp_err()
        try:
            obj.inject_completer_abort_err()
        except ModuleNotFoundError:
            pass
        obj.inject_cto_err()
        obj.ack()
        obj.nak()
        obj.inject_ur_err()
        obj.bad_ecrc()
        obj.poisoned_tlp()
        obj.stop_ack()
        try:
            obj.start_ack()
        except NotImplementedError:
            pass
        obj.malformed_tlp()
        obj.surprise_link_down()
        try:
            obj.crs()
        except NotImplementedError:
            pass
        obj.unexpected_completion()
        obj.flow_ctrl_protocol_err()
