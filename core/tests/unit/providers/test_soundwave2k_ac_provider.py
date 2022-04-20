import six

if six.PY2:
    import mock

if six.PY3 or six.PY34:
    from unittest import mock
from dtaf_core.providers.internal.soundwave2k_ac_provider import Soundwave2kAcProvider

from xml.etree import ElementTree as ET

cfgs = [
    ET.fromstring("""
   <ac>
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
    </ac>
"""), {
        "ac": {
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
    @mock.patch('dtaf_core.providers.internal.soundwave2k_ac_provider.DriverFactory')
    def test_ac_power_on(driver_mock):
        for cfg in cfgs:
            with Soundwave2kAcProvider(cfg, _Log()) as obj:
                obj.__port = mock.Mock()
                obj.ac_power_on()

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.soundwave2k_ac_provider.DriverFactory')
    def test_ac_power_off(driver_mock):
        for cfg in cfgs:
            with Soundwave2kAcProvider(cfg, _Log()) as obj:
                obj.__port = mock.Mock()
                obj.ac_power_off()

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.soundwave2k_ac_provider.DriverFactory')
    def test_get_ac_power_state(driver_mock):
        for cfg in cfgs:
            with Soundwave2kAcProvider(cfg, _Log()) as obj:
                obj.__port = mock.Mock()
                obj.get_ac_power_state()

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.soundwave2k_ac_provider.DriverFactory')
    def test_set_username_password(driver_mock):
        for cfg in cfgs:
            with Soundwave2kAcProvider(cfg, _Log()) as obj:
                obj.__port = mock.Mock()
                try:
                    obj.set_username_password()
                except NotImplementedError:
                    return

    @staticmethod
    @mock.patch('dtaf_core.providers.internal.soundwave2k_ac_provider.DriverFactory')
    def test_reset_username_password(driver_mock):
        for cfg in cfgs:
            with Soundwave2kAcProvider(cfg, _Log()) as obj:
                obj.__port = mock.Mock()
                try:
                    obj.reset_username_password()
                except NotImplementedError:
                    return
