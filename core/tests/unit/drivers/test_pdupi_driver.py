from dtaf_core.drivers.internal.pdupi_driver import PdupiDriver
from xml.etree import ElementTree as ET
import mock
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


cfg_normal = ET.fromstring("""
    <pdupi>
        <ip>10.190.155.147</ip>
        <port>80</port>
        <proxy>http://child-prc.intel.com:913</proxy>
        <channel>ch1</channel>
        <username>admin</username>
        <password>intel@123</password>
        <masterkey>smartrpipdu</masterkey>
    </pdupi>     
""")


class TestPduPiDriver(object):
    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.pdupi_driver.time.sleep")
    @mock.patch("dtaf_core.drivers.internal.pdupi_driver.subprocess.check_output")
    def test_dc_power_on(chkMock, slMock):
        chkMock.side_effect = [b"Power ON", TypeError("UT")]
        with PdupiDriver(cfg_normal, _Log()) as pi: #type: PdupiDriver
            assert pi.dc_power_on(timeout=10)
            has_exception = False
            try:
                pi.dc_power_on(timeout=10)
            except Exception as e:
                has_exception = True
            assert has_exception

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.pdupi_driver.time.sleep")
    @mock.patch("dtaf_core.drivers.internal.pdupi_driver.subprocess.check_output")
    def test_dc_power_off(chkMock, slMock):
        chkMock.side_effect = [b"Power OFF", TypeError("UT")]
        with PdupiDriver(cfg_normal, _Log()) as pi:  # type: PdupiDriver
            assert pi.dc_power_off(timeout=10)
            has_exception = False
            try:
                pi.dc_power_off(timeout=10)
            except Exception as e:
                has_exception = True
            assert has_exception

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.pdupi_driver.time.sleep")
    @mock.patch("dtaf_core.drivers.internal.pdupi_driver.subprocess.check_output")
    def test_get_dc_power_state(chkMock, slMock):
        chkMock.side_effect = [b"Detected", TypeError("UT")]
        with PdupiDriver(cfg_normal, _Log()) as pi:  # type: PdupiDriver
            assert pi.get_dc_power_state()
            has_exception = False
            try:
                pi.get_dc_power_state()
            except Exception as e:
                has_exception = True
            assert has_exception

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.pdupi_driver.time.sleep")
    @mock.patch("dtaf_core.drivers.internal.pdupi_driver.subprocess.check_output")
    def test_dc_power_reset(chkMock, slMock):
        chkMock.side_effect = [b"Reboot", TypeError("UT")]
        with PdupiDriver(cfg_normal, _Log()) as pi:  # type: PdupiDriver
            assert pi.dc_power_reset()
            has_exception = False
            try:
                pi.dc_power_reset()
            except Exception as e:
                has_exception = True
            assert has_exception

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.pdupi_driver.time.sleep")
    @mock.patch("dtaf_core.drivers.internal.pdupi_driver.subprocess.check_output")
    def test_ac_power_on(chkMock, slMock):
        chkMock.side_effect = [b"Power ON", TypeError("UT")]
        with PdupiDriver(cfg_normal, _Log()) as pi:  # type: PdupiDriver
            assert pi.ac_power_on(timeout=10)
            has_exception = False
            try:
                pi.ac_power_on(timeout=10)
            except Exception as e:
                has_exception = True
            assert has_exception

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.pdupi_driver.time.sleep")
    @mock.patch("dtaf_core.drivers.internal.pdupi_driver.subprocess.check_output")
    def test_ac_power_off(chkMock, slMock):
        chkMock.side_effect = [b"Power OFF", TypeError("UT")]
        with PdupiDriver(cfg_normal, _Log()) as pi:  # type: PdupiDriver
            assert pi.ac_power_off(timeout=10)
            has_exception = False
            try:
                pi.ac_power_off(timeout=10)
            except Exception as e:
                has_exception = True
            assert has_exception

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.pdupi_driver.time.sleep")
    @mock.patch("dtaf_core.drivers.internal.pdupi_driver.subprocess.check_output")
    def test_get_ac_power_state(chkMock, slMock):
        chkMock.side_effect = [b"Detected", TypeError("UT")]
        with PdupiDriver(cfg_normal, _Log()) as pi:  # type: PdupiDriver
            assert pi.get_ac_power_state()
            has_exception = False
            try:
                pi.get_ac_power_state()
            except Exception as e:
                has_exception = True
            assert has_exception

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.pdupi_driver.time.sleep")
    @mock.patch("dtaf_core.drivers.internal.pdupi_driver.subprocess.check_output")
    def test_set_username_password(chkMock, slMock):
        chkMock.side_effect = ["OK", TypeError("UT")]
        with PdupiDriver(cfg_normal, _Log()) as pi:  # type: PdupiDriver
            assert pi.set_username_password(channel="ch1", username="test", password="psw")
            has_exception = False
            try:
                pi.set_username_password(channel="ch1", username="test", password="psw")
            except Exception as e:
                has_exception = True
            assert has_exception

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.pdupi_driver.time.sleep")
    @mock.patch("dtaf_core.drivers.internal.pdupi_driver.subprocess.check_output")
    def test_reset_username_password(chkMock, slMock):
        chkMock.side_effect = [b"UserName and Password Removed", TypeError("UT")]
        with PdupiDriver(cfg_normal, _Log()) as pi:  # type: PdupiDriver
            assert pi.reset_username_password(channel="ch1", master_passkey="test")
            has_exception = False
            try:
                pi.reset_username_password(channel="ch1", master_passkey="test")
            except Exception as e:
                has_exception = True
            assert has_exception
