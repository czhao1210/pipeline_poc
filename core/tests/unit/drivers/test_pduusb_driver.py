from dtaf_core.drivers.internal.pduusb_driver import PduusbDriver,BasePduusbDriver
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
        <pduusb>
            <ip>10.190.155.174</ip>
            <port>80</port>
            <proxy>http://child-prc.intel.com:913</proxy>
            <image_name>xeon-d.bin</image_name>
        </pduusb>    
""")


class TestPiDriver(object):

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.pi_driver.subprocess.check_output")
    def test_remove_power(chkMock):
        chkMock.side_effect = [b"Power Turned ON and Verified", TypeError("UT")]
        with PduusbDriver(cfg_normal, _Log()) as pduusb:  # type: PduusbDriver
            pduusb.remove_power()

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.pi_driver.subprocess.check_output")
    def test_connect_power(chkMock):
        chkMock.side_effect = [b"Power Turned ON and Verified", TypeError("UT")]
        with PduusbDriver(cfg_normal, _Log()) as pduusb:  # type: PduusbDriver
            pduusb.connect_power()

    @staticmethod
    @mock.patch("dtaf_core.drivers.internal.pi_driver.subprocess.check_output")
    def test_ac_connected(chkMock):
        chkMock.side_effect = [b"Power Turned ON and Verified", TypeError("UT")]
        with PduusbDriver(cfg_normal, _Log()) as pduusb:  # type: PduusbDriver
            try:
                pduusb.ac_connected()
            except NotImplementedError:
                return

