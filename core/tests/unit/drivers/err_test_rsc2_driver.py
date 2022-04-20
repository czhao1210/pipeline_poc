import six
if six.PY2:
    import mock
if six.PY3:
    from unittest import mock

from dtaf_core.drivers.internal.rsc2_driver import Rsc2Driver
import xml.etree.ElementTree as ET

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

log = _Log

cnf_normal = ET.fromstring("""
                        <redfish>
                            <ip>10.239.181.130</ip>
                            <username>root</username>
							<password>0penBmc</password>
							<image_name>demo.rom</image_name>
                        </redfish>
""")


class TestRsc2Driver():

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.rsc2_driver.subprocess.check_output')
    def test_press_power_button(mymock):
        mymock.return_value = "rsc2_return_bool=True".encode('utf-8')
        obj = Rsc2Driver(cfg_opts=cnf_normal, log=log)
        obj.press_power_button(10)

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.rsc2_driver.subprocess.check_output')
    def test_press_reset_button(mymock):
        mymock.return_value = "rsc2_return_bool=True".encode('utf-8')
        obj = Rsc2Driver(cfg_opts=cnf_normal, log=log)
        obj.press_reset_button()

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.rsc2_driver.subprocess.check_output')
    def test_remove_power(mymock):
        mymock.return_value = "rsc2_return_bool=True".encode('utf-8')
        obj = Rsc2Driver(cfg_opts=cnf_normal, log=log)
        obj.remove_power()

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.rsc2_driver.subprocess.check_output')
    def test_connect_power(mymock):
        mymock.return_value = "rsc2_return_bool=True".encode('utf-8')
        obj = Rsc2Driver(cfg_opts=cnf_normal, log=log)
        obj.connect_power()

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.rsc2_driver.subprocess.check_output')
    def test_ac_connected(mymock):
        mymock.return_value = "rsc2_return_bool=True".encode('utf-8')
        obj = Rsc2Driver(cfg_opts=cnf_normal, log=log)
        try:
            obj.ac_connected()
        except:
            pass

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.rsc2_driver.subprocess.check_output')
    def test_connect_usb_to_sut(mymock):
        mymock.return_value = "rsc2_return_bool=True".encode('utf-8')
        obj = Rsc2Driver(cfg_opts=cnf_normal, log=log)
        obj.connect_usb_to_sut()

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.rsc2_driver.subprocess.check_output')
    def test_connect_usb_to_host(mymock):
        mymock.return_value = "rsc2_return_bool=True".encode('utf-8')
        obj = Rsc2Driver(cfg_opts=cnf_normal, log=log)
        obj.connect_usb_to_host()

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.rsc2_driver.subprocess.check_output')
    def test_disconnect_usb(mymock):
        mymock.return_value = "rsc2_return_bool=True".encode('utf-8')
        obj = Rsc2Driver(cfg_opts=cnf_normal, log=log)
        obj.disconnect_usb()

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.rsc2_driver.subprocess.check_output')
    def test_read_power_led(mymock):
        mymock.return_value = "rsc2_return_bool=True".encode('utf-8')
        obj = Rsc2Driver(cfg_opts=cnf_normal, log=log)
        try:
            obj.read_power_led()
        except:
            pass

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.rsc2_driver.subprocess.check_output')
    def test_read_amber_status_led(mymock):
        mymock.return_value = "rsc2_return_bool=True".encode('utf-8')
        obj = Rsc2Driver(cfg_opts=cnf_normal, log=log)
        try:
            obj.read_amber_status_led()
        except:
            pass

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.rsc2_driver.subprocess.check_output')
    def test_read_id_led(mymock):
        mymock.return_value = "rsc2_return_bool=True".encode('utf-8')
        obj = Rsc2Driver(cfg_opts=cnf_normal, log=log)
        try:
            obj.read_id_led()
        except:
            pass