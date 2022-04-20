import xml.etree.ElementTree as ET
from dtaf_core.drivers.internal.raspberry_driver import RaspberryDriver
import pytest
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


log = _Log()

cnf_normal = ET.fromstring("""
                        <redfish>
                            <ip>10.239.181.130</ip>
                            <username>root</username>
							<password>0penBmc</password>
							<image_name>demo.rom</image_name>
                        </redfish>
""")


class RaiseError():
    def Exception_error(self):
        raise Exception('My error.')


class TestRaspberryDriver(object):
    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.raspberry_driver.subprocess')
    @pytest.mark.parametrize("error", [True, False])
    def test_ac_power_on(subprocess_mock, error):
        if error:
            subprocess_mock.check_output = RaiseError().Exception_error
        else:
            subprocess_mock.check_output.return_value = b'Power Turned ON and Verified'
        with RaspberryDriver(log, cnf_normal) as rd_obj:
            try:
                rd_obj.ac_power_on()
            except:
                pass

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.raspberry_driver.subprocess')
    @pytest.mark.parametrize("error", [True, False])
    def test_ac_power_off(subprocess_mock, error):
        if error:
            subprocess_mock.check_output = RaiseError().Exception_error
        else:
            subprocess_mock.check_output.return_value = b'Power Turned OFF and Verified'
        with RaspberryDriver(log, cnf_normal) as rd_obj:
            try:
                rd_obj.ac_power_off()
            except:
                pass

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.raspberry_driver.subprocess')
    @pytest.mark.parametrize("error", [True, False])
    def test_get_ac_power_state(subprocess_mock, error):
        if error:
            subprocess_mock.check_output = RaiseError().Exception_error
        else:
            subprocess_mock.check_output.return_value = b'AC power detected'
        with RaspberryDriver(log, cnf_normal) as rd_obj:
            try:
                rd_obj.get_ac_power_state()
            except:
                pass

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.raspberry_driver.subprocess')
    @pytest.mark.parametrize("error", [True, False])
    def test_dc_power_on(subprocess_mock, error):
        if error:
            subprocess_mock.check_output = RaiseError().Exception_error
        else:
            subprocess_mock.check_output.return_value = b'Dc Power Turned ON and Verfied'
        with RaspberryDriver(log, cnf_normal) as rd_obj:
            try:
                rd_obj.dc_power_on()
            except:
                pass

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.raspberry_driver.subprocess')
    @pytest.mark.parametrize("error", [True, False])
    def test_dc_power_off(subprocess_mock, error):
        if error:
            subprocess_mock.check_output = RaiseError().Exception_error
        else:
            subprocess_mock.check_output.return_value = b'DC Power Turned OFF and Verified'
        with RaspberryDriver(log, cnf_normal) as rd_obj:
            try:
                rd_obj.dc_power_off()
            except:
                pass

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.raspberry_driver.subprocess')
    @pytest.mark.parametrize("error", [True, False])
    def test_get_dc_power_state(subprocess_mock, error):
        if error:
            subprocess_mock.check_output = RaiseError().Exception_error
        else:
            subprocess_mock.check_output.return_value = b'DC power detected'
        with RaspberryDriver(log, cnf_normal) as rd_obj:
            try:
                rd_obj.get_dc_power_state()
            except:
                pass

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.raspberry_driver.subprocess')
    @pytest.mark.parametrize("error", [True, False])
    def test_dc_power_reset(subprocess_mock, error):
        if error:
            subprocess_mock.check_output = RaiseError().Exception_error
        else:
            subprocess_mock.check_output.return_value = b'Reboot Command Issued'
        with RaspberryDriver(log, cnf_normal) as rd_obj:
            try:
                rd_obj.dc_power_reset()
            except:
                pass

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.raspberry_driver.subprocess')
    @pytest.mark.parametrize("error", [True, False])
    def test_connect_usb_to_sut(subprocess_mock, error):
        if error:
            subprocess_mock.check_output = RaiseError().Exception_error
        else:
            subprocess_mock.check_output.return_value = b'USB Switch to SUT Done'
        with RaspberryDriver(log, cnf_normal) as rd_obj:
            try:
                rd_obj.connect_usb_to_sut()
            except:
                pass

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.raspberry_driver.subprocess')
    @pytest.mark.parametrize("error", [True, False])
    def test_connect_usb_to_host(subprocess_mock, error):
        if error:
            subprocess_mock.check_output = RaiseError().Exception_error
        else:
            subprocess_mock.check_output.return_value = b'USB Switch to Host Done'
        with RaspberryDriver(log, cnf_normal) as rd_obj:
            try:
                rd_obj.connect_usb_to_host()
            except:
                pass

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.raspberry_driver.subprocess')
    @pytest.mark.parametrize("error", [True, False])
    def test_disconnect_usb(subprocess_mock, error):
        if error:
            subprocess_mock.check_output = RaiseError().Exception_error
        else:
            subprocess_mock.check_output.return_value = b'USB Disconnect Done'
        with RaspberryDriver(log, cnf_normal) as rd_obj:
            try:
                rd_obj.disconnect_usb()
            except:
                pass

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.raspberry_driver.subprocess')
    @pytest.mark.parametrize("error", [True, False])
    def test_set_clear_cmos(subprocess_mock, error):
        if error:
            subprocess_mock.check_output = RaiseError().Exception_error
        else:
            subprocess_mock.check_output.return_value = b'ClearCmos Command Issued'
        with RaspberryDriver(log, cnf_normal) as rd_obj:
            try:
                rd_obj.set_clear_cmos()
            except:
                pass

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.raspberry_driver.subprocess')
    @pytest.mark.parametrize("error", [True, False])
    def test_read_post_code(subprocess_mock, error):
        if error:
            subprocess_mock.check_output = RaiseError().Exception_error
        else:
            subprocess_mock.check_output.return_value = "123"
        with RaspberryDriver(log, cnf_normal) as rd_obj:
            try:
                rd_obj.read_post_code()
            except:
                pass

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.raspberry_driver.subprocess')
    @pytest.mark.parametrize("error", [True, False])
    def test_read_s3_pin(subprocess_mock, error):
        if error:
            subprocess_mock.check_output = RaiseError().Exception_error
        else:
            subprocess_mock.check_output.return_value = b'S3 power detected'
        with RaspberryDriver(log, cnf_normal) as rd_obj:
            try:
                rd_obj.read_s3_pin()
            except:
                pass

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.raspberry_driver.subprocess')
    @pytest.mark.parametrize("error", [True, False])
    def test_read_s4_pin(subprocess_mock, error):
        if error:
            subprocess_mock.check_output = RaiseError().Exception_error
        else:
            subprocess_mock.check_output.return_value = b'S4 power detected'
        with RaspberryDriver(log, cnf_normal) as rd_obj:
            try:
                rd_obj.read_s4_pin()
            except:
                pass

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.raspberry_driver.subprocess')
    @pytest.mark.parametrize("error", [True, False])
    def test_program_jumper(subprocess_mock, error):
        if error:
            subprocess_mock.check_output = RaiseError().Exception_error
        else:
            subprocess_mock.check_output.return_value = b'Jumper set Done'
        with RaspberryDriver(log, cnf_normal) as rd_obj:
            try:
                rd_obj.program_jumper(1, 2)
            except:
                pass
