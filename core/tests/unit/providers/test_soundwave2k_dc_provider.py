import six

if six.PY2:
    import mock

if six.PY3 or six.PY34:
    from unittest import mock
from dtaf_core.providers.internal.soundwave2k_dc_provider import Soundwave2kDcProvider
from dtaf_core.lib.exceptions import DriverIOError

from xml.etree import ElementTree as ET
import pytest

cfgs = [
    ET.fromstring("""
   <dc>
                    <driver>
                        <soundwave2k enable_s3_detect="False">
                            <baudrate>115200</baudrate>
                            <serial type="1" />
                            <port>COM101</port>
                            <voltagethreholds>
                                <main_power>
                                    <low>0.8</low>
                                    <high>2.85</high>
                                </main_power>
                                <dsw>
                                    <low>0.8</low>
                                    <high>2.85</high>
                                </dsw>
                                <memory>
                                    <low>0.3</low>
                                    <high>2.2</high>
                                </memory>
                            </voltagethreholds>
                        </soundwave2k>
                    </driver>
                    <timeout>
                        <power_on>5</power_on>
                        <power_off>20</power_off>
                    </timeout>
                </dc>
"""), {
        "dc": {
            "driver": {
                "soundwave2k": {
                    "@enable_s3_detect": "False",
                    "baudrate": "115200",
                    "serial": {
                        "@type": "1"
                    },
                    "port": "COM101",
                    "voltagethreholds": {
                        "main_power": {
                            "low": "0.8",
                            "high": "2.85"
                        },
                        "dsw": {
                            "low": "0.8",
                            "high": "2.85"
                        },
                        "memory": {
                            "low": "0.3",
                            "high": "2.2"
                        }
                    }
                }
            },
            "timeout": {
                "power_on": "5",
                "power_off": "20"
            }
        }
    }
]


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


class TestSuites:
    @staticmethod
    @mock.patch('dtaf_core.providers.internal.soundwave2k_dc_provider.DriverFactory')
    def test_dc_power_on(driver_mock):
        for cfg in cfgs:
            with Soundwave2kDcProvider(cfg, _Log()) as obj:
                obj.__port = mock.Mock()
                obj.dc_power_on()

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.soundwave2k_dc_provider.DriverFactory')
    def test_dc_power_off(driver_mock):
        for cfg in cfgs:
            with Soundwave2kDcProvider(cfg, _Log()) as obj:
                obj.__port = mock.Mock()
                obj.dc_power_off()

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.soundwave2k_dc_provider.DriverFactory')
    @pytest.mark.parametrize("press_reset_button_return,release_reset_button_return", [(True, False), (False, True)])
    def test_dc_power_reset(driver_mock, press_reset_button_return, release_reset_button_return):
        driver_mock.create.return_value.press_reset_button.return_value = press_reset_button_return
        driver_mock.create.return_value.release_reset_button.return_value = release_reset_button_return

        for cfg in cfgs:
            with Soundwave2kDcProvider(cfg, _Log()) as obj:
                obj.__port = mock.Mock()
                obj.dc_power_reset()

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.soundwave2k_dc_provider.DriverFactory')
    @pytest.mark.parametrize("return_list,enable_s3_detect_value",
                             [([3, 3, 3], True), ([0, 3, 3], True), ([0, 3, 0], True), ([0, 0, 0], True),
                              ([3, 3], False), ([0, 3], False), ([0, 0], False)])
    def test_get_dc_power_state(driver_mock, return_list, enable_s3_detect_value):
        driver_mock.create.return_value.__enter__.return_value.get_voltages.return_value = return_list
        for cfg in cfgs:
            with Soundwave2kDcProvider(cfg, _Log()) as obj:
                obj._config_model.driver_cfg.enable_s3_detect = enable_s3_detect_value
                obj.__port = mock.Mock()
                try:
                    obj.get_dc_power_state()
                except DriverIOError:
                    pass

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.soundwave2k_dc_provider.DriverFactory')
    @pytest.mark.parametrize('pop_val', ["_Soundwave2kDriverConfig__low_main_power_voltage",
                                         "_Soundwave2kDriverConfig__high_main_power_voltage",
                                         "_Soundwave2kDriverConfig__high_memory_voltage",
                                         "_Soundwave2kDriverConfig__low_memory_voltage"])
    def test_get_dc_power_state_error(driver_mock, pop_val):
        for cfg in cfgs:
            with Soundwave2kDcProvider(cfg, _Log()) as obj:
                obj._config_model.driver_cfg.__dict__.pop(pop_val)
                obj.__port = mock.Mock()
                try:
                    obj.get_dc_power_state()
                except DriverIOError:
                    return
