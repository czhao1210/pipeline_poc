from dtaf_core.drivers.internal.pi_driver import PiDriver
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
        <pi>
            <ip>10.190.155.174</ip>
            <port>80</port>
            <username>username</username>
            <password>password</password>
            <type>type</type>
            <proxy>http://child-prc.intel.com:913</proxy>
            <image_name>xeon-d.bin</image_name>
        </pi>    
""")


class TestPiDriver(object):
    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.pi_driver.subprocess.check_output")
    def test_ac_power_on(chkMock):
        chkMock.side_effect = [b"Power Turned ON and Verified", TypeError("UT")]
        with PiDriver(cfg_normal, _Log()) as pi: #type: PiDriver
            assert pi.ac_power_on(10)
            has_exception = False
            try:
                pi.ac_power_on(10)
            except Exception as e:
                has_exception = True
            assert has_exception

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.pi_driver.subprocess.check_output")
    def test_ac_power_off(chkMock):
        chkMock.side_effect = [b"Power Turned OFF and Verified", TypeError("UT")]
        with PiDriver(cfg_normal, _Log()) as pi: #type: PiDriver
            assert pi.ac_power_off(10)
            has_exception = False
            try:
                pi.ac_power_off(10)
            except Exception as e:
                has_exception = True
            assert has_exception

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.pi_driver.subprocess.check_output")
    def test_get_ac_power_state(chkMock):
        chkMock.side_effect = [b"AC power detected", TypeError("UT")]
        with PiDriver(cfg_normal, _Log()) as pi: #type: PiDriver
            assert pi.get_ac_power_state()
            has_exception = False
            try:
                pi.get_ac_power_state()
            except Exception as e:
                has_exception = True
            assert has_exception

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.pi_driver.subprocess.check_output")
    def test_dc_power_on(chkMock):
        chkMock.side_effect = [b"Dc Power Turned ON and Verfied", TypeError("UT")]
        with PiDriver(cfg_normal, _Log()) as pi: #type: PiDriver
            assert pi.dc_power_on(10)
            has_exception = False
            try:
                assert pi.dc_power_on(10)
            except Exception as e:
                has_exception = True
            assert has_exception

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.pi_driver.subprocess.check_output")
    def test_dc_power_off(chkMock):
        chkMock.side_effect = [b"DC Power Turned OFF and Verified", TypeError("UT")]
        with PiDriver(cfg_normal, _Log()) as pi: #type: PiDriver
            assert pi.dc_power_off(10)
            has_exception = False
            try:
                assert pi.dc_power_off(10)
            except Exception as e:
                has_exception = True
            assert has_exception

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.pi_driver.subprocess.check_output")
    def test_get_dc_power_state(chkMock):
        chkMock.side_effect = [b"DC power detected", TypeError("UT")]
        with PiDriver(cfg_normal, _Log()) as pi: #type: PiDriver
            assert pi.get_dc_power_state()
            has_exception = False
            try:
                assert pi.get_dc_power_state()
            except Exception as e:
                has_exception = True
            assert has_exception

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.pi_driver.subprocess.check_output")
    def test_dc_power_reset(chkMock):
        chkMock.side_effect = [b"Reboot Command Issued", TypeError("UT")]
        with PiDriver(cfg_normal, _Log()) as pi: #type: PiDriver
            assert pi.dc_power_reset()
            has_exception = False
            try:
                assert pi.dc_power_reset()
            except Exception as e:
                has_exception = True
            assert has_exception

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.pi_driver.subprocess.check_output")
    def test_connect_usb_to_sut(chkMock):
        chkMock.side_effect = [b"USB Switch to SUT Done", TypeError("UT")]
        with PiDriver(cfg_normal, _Log()) as pi: #type: PiDriver
            assert pi.connect_usb_to_sut()
            has_exception = False
            try:
                assert pi.connect_usb_to_sut()
            except Exception as e:
                has_exception = True
            assert has_exception

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.pi_driver.subprocess.check_output")
    def test_connect_usb_to_host(chkMock):
        chkMock.side_effect = [b"USB Switch to Host Done", TypeError("UT")]
        with PiDriver(cfg_normal, _Log()) as pi: #type: PiDriver
            assert pi.connect_usb_to_host()
            has_exception = False
            try:
                assert pi.connect_usb_to_host()
            except Exception as e:
                has_exception = True
            assert has_exception

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.pi_driver.subprocess.check_output")
    def test_disconnect_usb(chkMock):
        chkMock.side_effect = [b"USB Disconnect Done", TypeError("UT")]
        with PiDriver(cfg_normal, _Log()) as pi: #type: PiDriver
            assert pi.disconnect_usb()
            has_exception = False
            try:
                assert pi.disconnect_usb()
            except Exception as e:
                has_exception = True
            assert has_exception

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.pi_driver.subprocess.check_output")
    def test_set_clear_cmos(chkMock):
        chkMock.side_effect = [b"ClearCmos Command Issued", TypeError("UT")]
        with PiDriver(cfg_normal, _Log()) as pi: #type: PiDriver
            assert pi.set_clear_cmos()
            has_exception = False
            try:
                assert pi.set_clear_cmos(10)
            except Exception as e:
                has_exception = True
            assert has_exception

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.pi_driver.subprocess.check_output")
    def test_read_postcode(chkMock):
        chkMock.side_effect = [b"8888", TypeError("UT")]
        with PiDriver(cfg_normal, _Log()) as pi: #type: PiDriver
            assert pi.read_postcode()
            has_exception = False
            try:
                assert pi.read_postcode()
            except Exception as e:
                has_exception = True
            assert has_exception

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.pi_driver.subprocess.check_output")
    def test_read_s3_pin(chkMock):
        chkMock.side_effect = [b"S3 power detected", TypeError("UT")]
        with PiDriver(cfg_normal, _Log()) as pi: #type: PiDriver
            assert pi.read_s3_pin()
            has_exception = False
            try:
                assert pi.read_s3_pin()
            except Exception as e:
                has_exception = True
            assert has_exception

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.pi_driver.subprocess.check_output")
    def test_read_s4_pin(chkMock):
        chkMock.side_effect = [b"S4 power detected", TypeError("UT")]
        with PiDriver(cfg_normal, _Log()) as pi: #type: PiDriver
            assert pi.read_s4_pin()
            has_exception = False
            try:
                assert pi.read_s4_pin()
            except Exception as e:
                has_exception = True
            assert has_exception

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.pi_driver.subprocess.check_output")
    def test_chip_identify(chkMock):
        chkMock.side_effect = [b"True", TypeError("UT")]
        with PiDriver(cfg_normal, _Log()) as pi: #type: PiDriver
            assert pi.chip_identify()
            has_exception = False
            try:
                assert pi.chip_identify()
            except Exception as e:
                has_exception = True
            assert has_exception

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.pi_driver.subprocess.check_output")
    def test_chip_reading(chkMock):
        chkMock.side_effect = [b"True", TypeError("UT")]
        with PiDriver(cfg_normal, _Log()) as pi: #type: PiDriver
            assert pi.chip_reading()
            has_exception = False
            try:
                assert pi.chip_reading()
            except Exception as e:
                has_exception = True
            assert has_exception

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.pi_driver.subprocess.check_output")
    def test_chip_flash(chkMock):
        chkMock.side_effect = [b"True", TypeError("UT")]
        with PiDriver(cfg_normal, _Log()) as pi: #type: PiDriver
            has_exception = False
            try:
                assert pi.chip_flash("test")
            except Exception as e:
                has_exception = True
            assert has_exception
