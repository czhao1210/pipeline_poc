from unittest import mock
from xml.etree import ElementTree as ET

import pytest

from dtaf_core.drivers.internal.ipmi_driver import IpmiDriver


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


log = _Log

cfg_normal = ET.fromstring("""
            <ipmi>
                    <ip>10.239.181.70</ip>
                    <username>root</username>
                    <password>0penBmc1</password>
                    <cmd>ipmitool.exe</cmd>
            </ipmi>
""")


class StdoutMock():
    def __init__(self, return_value):
        self.return_value = return_value

    def read(self):
        if self.return_value == "raise":
            raise Exception
        else:
            return self.return_value


class PopenMock():
    def __init__(self, find_return_value):
        self.find_return_value = find_return_value
        self.stdout = StdoutMock(self.find_return_value)


class TestIpmiDriver:

    @staticmethod
    @mock.patch('drivers.internal.ipmi_driver.subprocess.Popen')
    @pytest.mark.parametrize('find_return_value', ['raise', 'Chassis Power Control: Up/On', 'error'])
    def test_dc_power_on(mymock, find_return_value):
        mymock.return_value = PopenMock(find_return_value)
        try:
            with IpmiDriver(cfg_opts=cfg_normal, log=log) as id_obj:
                id_obj.dc_power_on(timeout=10)
        except Exception:
            pass

    @staticmethod
    @mock.patch('drivers.internal.ipmi_driver.subprocess.Popen')
    @pytest.mark.parametrize('find_return_value', ['Chassis Power Control: Down/Off',
                                                   'Set Chassis Power Control to Down/Off failed: Command not supported in present state',
                                                   'raise', 'error'])
    def test_dc_power_off(mymock, find_return_value):
        mymock.return_value = PopenMock(find_return_value)
        try:
            with IpmiDriver(cfg_opts=cfg_normal, log=log) as id_obj:
                id_obj.dc_power_off(10)
        except Exception:
            pass

    @staticmethod
    @mock.patch('drivers.internal.ipmi_driver.subprocess.Popen')
    @pytest.mark.parametrize('find_return_value', ['Chassis Power is on', 'raise', 'error'])
    def test_get_dc_power_state(mymock, find_return_value):
        mymock.return_value = PopenMock(find_return_value)
        try:
            with IpmiDriver(cfg_opts=cfg_normal, log=log) as id_obj:
                id_obj.get_dc_power_state()
        except Exception:
            pass

    @staticmethod
    @mock.patch('drivers.internal.ipmi_driver.subprocess.Popen')
    @pytest.mark.parametrize('find_return_value', ['Chassis Power Control: Reset',
                                                   'Set Chassis Power Control to Reset failed: Command not supported in present state',
                                                   'raise', 'error'])
    def test_dc_power_reset(mymock, find_return_value):
        mymock.return_value = PopenMock(find_return_value)
        try:
            with IpmiDriver(cfg_opts=cfg_normal, log=log) as id_obj:
                id_obj.dc_power_reset()
        except Exception:
            pass

    @staticmethod
    @mock.patch('drivers.internal.ipmi_driver.subprocess.Popen')
    @pytest.mark.parametrize('find_return_value', ['raise', 'error', 'hassis Power is on'])
    def test_execute(mymock, find_return_value):
        mymock.return_value = PopenMock(find_return_value)
        try:
            with IpmiDriver(cfg_opts=cfg_normal, log=log) as id_obj:
                id_obj.execute()
        except Exception:
            pass
