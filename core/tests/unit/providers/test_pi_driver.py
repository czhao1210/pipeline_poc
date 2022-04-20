from __future__ import absolute_import
import pytest
import six

if six.PY2:
    import mock
    from mock import MagicMock
if six.PY3 or six.PY34:
    from unittest import mock
    from unittest.mock import MagicMock

from dtaf_core.drivers.internal.pi_driver import PiDriver


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


cfg_opts = None
log = _Log()


class Test_PiDriver(object):
    @staticmethod
    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.lib.private.drivercfg_factory.DriverCfgFactory.create')
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('ret, state, time',
                             [(b"Power Turned ON and Verified", True, 100),
                              (b"Power Turned", None, 100)])
    def test_ac_power_on(get_conf, driver, pcf, driver_cfg, check_output_mock, ret, time, state):
        check_output_mock.return_value = ret
        assert PiDriver(cfg_opts, log).ac_power_on(timeout=time) is state

    @staticmethod
    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.lib.private.drivercfg_factory.DriverCfgFactory.create')
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('ret, time, state',
                             [(MagicMock(side_effect=Exception("Test2")), MagicMock(return_value=100), "Test2")])
    def test_ac_power_on_exception(get_conf, driver, pcf, driver_cfg, check_output_mock, ret, time, state):
        check_output_mock.side_effect = ret
        with pytest.raises(Exception) as ex:
            PiDriver(cfg_opts, log).ac_power_on(timeout=time)
        assert str(ex.value) == state

    @staticmethod
    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.lib.private.drivercfg_factory.DriverCfgFactory.create')
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('ret, state, time',
                             [(b"Power Turned OFF and Verified", True, 100),
                              (b"incorrect output", None, 50)])
    def test_ac_power_off(get_conf, driver, pcf, driver_cfg, check_output_mock, ret, time, state):
        check_output_mock.return_value = ret
        assert PiDriver(cfg_opts, log).ac_power_off(timeout=time) is state

    @staticmethod
    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.lib.private.drivercfg_factory.DriverCfgFactory.create')
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('ret, time, state',
                             [(MagicMock(side_effect=Exception("Test2")), MagicMock(return_value=100), "Test2")])
    def test_ac_power_off_exception(get_conf, driver, pcf, driver_cfg, check_output_mock, ret, time, state):
        check_output_mock.side_effect = ret
        with pytest.raises(Exception) as ex:
            PiDriver(cfg_opts, log).ac_power_off(timeout=time)
        assert str(ex.value) == state

    @staticmethod
    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.lib.private.drivercfg_factory.DriverCfgFactory.create')
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('ret, state',
                             [(b"AC power detected", True),
                              (b"incorrect output", None)])
    def test_get_ac_power_state(get_conf, driver, pcf, driver_cfg, check_output_mock, ret, state):
        check_output_mock.return_value = ret
        assert PiDriver(cfg_opts, log).get_ac_power_state() is state

    @staticmethod
    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.lib.private.drivercfg_factory.DriverCfgFactory.create')
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('ret, state',
                             [(MagicMock(side_effect=Exception("Test2")), "Test2")])
    def test_get_ac_power_state_exception(get_conf, driver, pcf, driver_cfg, check_output_mock, ret, state):
        check_output_mock.side_effect = ret
        with pytest.raises(Exception) as ex:
            PiDriver(cfg_opts, log).get_ac_power_state()
        assert str(ex.value) == state

    @staticmethod
    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.lib.private.drivercfg_factory.DriverCfgFactory.create')
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('ret, state, time',
                             [(b"Dc Power Turned ON and Verfied", True, 100),
                              (b"incorrect output", None, 50)])
    def test_dc_power_on(get_conf, driver, pcf, driver_cfg, check_output_mock, ret, time, state):
        check_output_mock.return_value = ret
        assert PiDriver(cfg_opts, log).dc_power_on(timeout=time) is state

    @staticmethod
    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.lib.private.drivercfg_factory.DriverCfgFactory.create')
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('ret, time, state',
                             [(MagicMock(side_effect=Exception("Test2")), MagicMock(return_value=100), "Test2")])
    def test_dc_power_on_exception(get_conf, driver, pcf, driver_cfg, check_output_mock, ret, time, state):
        check_output_mock.side_effect = ret
        with pytest.raises(Exception) as ex:
            PiDriver(cfg_opts, log).dc_power_on(timeout=time)
        assert str(ex.value) == state

    @staticmethod
    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.lib.private.drivercfg_factory.DriverCfgFactory.create')
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('ret, state, time',
                             [(b"DC Power Turned OFF and Verified", True, 100),
                              (b"incorrect output", None, 50)])
    def test_dc_power_off(get_conf, driver, pcf, driver_cfg, check_output_mock, ret, time, state):
        check_output_mock.return_value = ret
        assert PiDriver(cfg_opts, log).dc_power_off(timeout=time) is state

    @staticmethod
    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.lib.private.drivercfg_factory.DriverCfgFactory.create')
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('ret, time, state',
                             [(MagicMock(side_effect=Exception("Test2")), MagicMock(return_value=100), "Test2")])
    def test_dc_power_off_exception(get_conf, driver, pcf, driver_cfg, check_output_mock, ret, time, state):
        check_output_mock.side_effect = ret
        with pytest.raises(Exception) as ex:
            PiDriver(cfg_opts, log).dc_power_off(timeout=time)
        assert str(ex.value) == state

    @staticmethod
    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.lib.private.drivercfg_factory.DriverCfgFactory.create')
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('ret, state',
                             [(b"DC power detected", True),
                              (b"incorrect output", None)])
    def test_get_dc_power_state(get_conf, driver, pcf, driver_cfg, check_output_mock, ret, state):
        check_output_mock.return_value = ret
        assert PiDriver(cfg_opts, log).get_dc_power_state() is state

    @staticmethod
    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.lib.private.drivercfg_factory.DriverCfgFactory.create')
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('ret, state',
                             [(MagicMock(side_effect=Exception("Test2")), "Test2")])
    def test_get_dc_power_state_exception(get_conf, driver, pcf, driver_cfg, check_output_mock, ret, state):
        check_output_mock.side_effect = ret
        with pytest.raises(Exception) as ex:
            PiDriver(cfg_opts, log).get_dc_power_state()
        assert str(ex.value) == state

    @staticmethod
    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.lib.private.drivercfg_factory.DriverCfgFactory.create')
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('ret, state, time',
                             [(b"USB Switch to SUT Done", True, 100),
                              (b"incorrect output", None, 50)])
    def test_connect_usb_to_sut(get_conf, driver, pcf, driver_cfg, check_output_mock, ret, time, state):
        check_output_mock.return_value = ret
        assert PiDriver(cfg_opts, log).connect_usb_to_sut(timeout=time) is state

    @staticmethod
    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.lib.private.drivercfg_factory.DriverCfgFactory.create')
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('ret, time, state',
                             [(MagicMock(side_effect=Exception("Test2")), MagicMock(return_value=100), "Test2")])
    def test_connect_usb_to_sut_exception(get_conf, driver, pcf, driver_cfg, check_output_mock, ret, time, state):
        check_output_mock.side_effect = ret
        with pytest.raises(Exception) as ex:
            PiDriver(cfg_opts, log).connect_usb_to_sut(timeout=time)
        assert str(ex.value) == state

    @staticmethod
    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.lib.private.drivercfg_factory.DriverCfgFactory.create')
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('ret, state, time',
                             [(b"USB Switch to Host Done", True, 100),
                              (b"incorrect output", None, 50)])
    def test_connect_usb_to_host(get_conf, driver, pcf, driver_cfg, check_output_mock, ret, time, state):
        check_output_mock.return_value = ret
        assert PiDriver(cfg_opts, log).connect_usb_to_host(timeout=time) is state

    @staticmethod
    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.lib.private.drivercfg_factory.DriverCfgFactory.create')
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('ret, time, state',
                             [(MagicMock(side_effect=Exception("Test2")), MagicMock(return_value=100), "Test2")])
    def test_connect_usb_to_host_exception(get_conf, driver, pcf, driver_cfg, check_output_mock, ret, time, state):
        check_output_mock.side_effect = ret
        with pytest.raises(Exception) as ex:
            PiDriver(cfg_opts, log).connect_usb_to_host(timeout=time)
        assert str(ex.value) == state

    @staticmethod
    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.lib.private.drivercfg_factory.DriverCfgFactory.create')
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('ret, state, time',
                             [(b"USB Disconnect Done", True, 100),
                              (b"incorrect output", None, 50)])
    def test_disconnect_usb(get_conf, driver, pcf, driver_cfg, check_output_mock, ret, time, state):
        check_output_mock.return_value = ret
        assert PiDriver(cfg_opts, log).disconnect_usb(timeout=time) is state

    @staticmethod
    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.lib.private.drivercfg_factory.DriverCfgFactory.create')
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('ret, time, state',
                             [(MagicMock(side_effect=Exception("Test2")), MagicMock(return_value=100), "Test2")])
    def test_disconnect_usb_exception(get_conf, driver, pcf, driver_cfg, check_output_mock, ret, time, state):
        check_output_mock.side_effect = ret
        with pytest.raises(Exception) as ex:
            PiDriver(cfg_opts, log).disconnect_usb(timeout=time)
        assert str(ex.value) == state

    @staticmethod
    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.lib.private.drivercfg_factory.DriverCfgFactory.create')
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('ret, state, time',
                             [(b"ClearCmos Command Issued", True, 100),
                              (b"incorrect output", None, 50)])
    def test_set_clear_cmos(get_conf, driver, pcf, driver_cfg, check_output_mock, ret, time, state):
        check_output_mock.return_value = ret
        assert PiDriver(cfg_opts, log).set_clear_cmos(timeout=time) is state

    @staticmethod
    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.lib.private.drivercfg_factory.DriverCfgFactory.create')
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('ret, time, state',
                             [(MagicMock(side_effect=Exception("Test2")), MagicMock(return_value=100), "Test2")])
    def test_set_clear_cmos_exception(get_conf, driver, pcf, driver_cfg, check_output_mock, ret, time, state):
        check_output_mock.side_effect = ret
        with pytest.raises(Exception) as ex:
            PiDriver(cfg_opts, log).set_clear_cmos(timeout=time)
        assert str(ex.value) == state

    @staticmethod
    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.lib.private.drivercfg_factory.DriverCfgFactory.create')
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('ret, state',
                             [(12, 12),
                              ('postcode', 'postcode')])
    def test_read_postcode(get_conf, driver, pcf, driver_cfg, check_output_mock, ret, state):
        check_output_mock.return_value = ret
        assert PiDriver(cfg_opts, log).read_postcode() is state

    @staticmethod
    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.lib.private.drivercfg_factory.DriverCfgFactory.create')
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('ret, state',
                             [(MagicMock(side_effect=Exception("Test2")), "Test2")])
    def test_read_postcode_exception(get_conf, driver, pcf, driver_cfg, check_output_mock, ret, state):
        check_output_mock.side_effect = ret
        with pytest.raises(Exception) as ex:
            PiDriver(cfg_opts, log).read_postcode()
        assert str(ex.value) == state

    @staticmethod
    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.lib.private.drivercfg_factory.DriverCfgFactory.create')
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('ret, state',
                             [(b"S3 power detected", True),
                              (b"incorrect output", None)])
    def test_read_s3_pin(get_conf, driver, pcf, driver_cfg, check_output_mock, ret, state):
        check_output_mock.return_value = ret
        assert PiDriver(cfg_opts, log).read_s3_pin() is state

    @staticmethod
    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.lib.private.drivercfg_factory.DriverCfgFactory.create')
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('ret, state',
                             [(MagicMock(side_effect=Exception("Test2")), "Test2")])
    def test_read_s3_pin_exception(get_conf, driver, pcf, driver_cfg, check_output_mock, ret, state):
        check_output_mock.side_effect = ret
        with pytest.raises(Exception) as ex:
            PiDriver(cfg_opts, log).read_s3_pin()
        assert str(ex.value) is state

    @staticmethod
    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.lib.private.drivercfg_factory.DriverCfgFactory.create')
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('ret, state',
                             [(b"S4 power detected", True),
                              (b"incorrect output", None)])
    def test_read_s4_pin(get_conf, driver, pcf, driver_cfg, check_output_mock, ret, state):
        check_output_mock.return_value = ret
        assert PiDriver(cfg_opts, log).read_s4_pin() is state

    @staticmethod
    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.lib.private.drivercfg_factory.DriverCfgFactory.create')
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('ret, state',
                             [(MagicMock(side_effect=Exception("Test2")), "Test2")])
    def test_read_s4_pin_exception(get_conf, driver, pcf, driver_cfg, check_output_mock, ret, state):
        check_output_mock.side_effect = ret
        with pytest.raises(Exception) as ex:
            PiDriver(cfg_opts, log).read_s4_pin()
        assert str(ex.value) == state

    @staticmethod
    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.lib.private.drivercfg_factory.DriverCfgFactory.create')
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('ret, st, pin, time, state',
                             [(b"Jumper set Done", "test1", 123, 100, True),
                              (b"Jumper unset Done", "test2", 123, 10, True),
                              (b"incorrect output", "test3", 123, 10, None)])
    def test_program_jumper(get_conf, driver, pcf, driver_cfg, check_output_mock, ret, st, pin, time, state):
        check_output_mock.return_value = ret
        assert PiDriver(cfg_opts, log).program_jumper(st, pin, time) is state

    @staticmethod
    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.lib.private.drivercfg_factory.DriverCfgFactory.create')
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('ret, st, pin, time, state',
                             [(MagicMock(side_effect=Exception("Test2")), 'test string', 1020, 100, "Test2")])
    def test_program_jumper_exception(get_conf, driver, pcf, driver_cfg, check_output_mock, ret, st, pin, time, state):
        check_output_mock.side_effect = ret
        with pytest.raises(Exception) as ex:
            PiDriver(cfg_opts, log).program_jumper(st, pin, time)
        assert str(ex.value) == state

    @staticmethod
    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.lib.private.drivercfg_factory.DriverCfgFactory.create')
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('ret, state',
                             [(b"incorrect output", None)])
    def test_chip_identify(get_conf, driver, pcf, driver_cfg, check_output_mock, ret, state):
        check_output_mock.return_value = ret
        assert PiDriver(cfg_opts, log).chip_identify() is state

    @staticmethod
    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.lib.private.drivercfg_factory.DriverCfgFactory.create')
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('ret, state',
                             [(MagicMock(side_effect=Exception("Test2")), "Test2")])
    def test_chip_identify_exception(get_conf, driver, pcf, driver_cfg, check_output_mock, ret, state):
        check_output_mock.side_effect = ret
        with pytest.raises(Exception) as ex:
            PiDriver(cfg_opts, log).chip_identify()
        assert str(ex.value) == state

    @staticmethod
    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.lib.private.drivercfg_factory.DriverCfgFactory.create')
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('ret, state',
                             [(b"incorrect output", None)])
    def test_chip_reading(get_conf, driver, pcf, driver_cfg, check_output_mock, ret, state):
        check_output_mock.return_value = ret
        assert PiDriver(cfg_opts, log).chip_reading() is state

    @staticmethod
    @mock.patch('subprocess.check_output')
    @mock.patch('dtaf_core.lib.private.drivercfg_factory.DriverCfgFactory.create')
    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
    @pytest.mark.parametrize('ret, state',
                             [(MagicMock(side_effect=Exception("Test2")), "Test2")])
    def test_chip_reading_exception(get_conf, driver, pcf, driver_cfg, check_output_mock, ret, state):
        check_output_mock.side_effect = ret
        with pytest.raises(Exception) as ex:
            PiDriver(cfg_opts, log).chip_reading()
        assert str(ex.value) == state

##    @staticmethod
##    @mock.patch('subprocess.check_output')
##    @mock.patch('dtaf_core.lib.private.drivercfg_factory.DriverCfgFactory.create')
##    @mock.patch('dtaf_core.drivers.driver_factory.DriverFactory.create')
##    @mock.patch('dtaf_core.lib.private.providercfg_factory.ProviderCfgFactory.create')
##    @mock.patch('dtaf_core.lib.configuration.ConfigurationHelper.get_driver_config')
##    @pytest.mark.parametrize('ret, path, image_name, state',
##                             [(b"Completed", 'path', 'image', True),(b"Incorrect", "path", 'image',None)])
##
##                              
##    def test_chip_flash(get_conf, driver, pcf, driver_cfg, check_output_mock, ret, path, image_name, state):
##        check_output_mock.return_value = ret
##        assert PiDriver(cfg_opts, log).chip_flash(path, image_name) is state
##

