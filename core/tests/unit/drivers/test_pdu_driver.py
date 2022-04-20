from xml.etree import ElementTree as ET

import mock
import pytest

from dtaf_core.drivers.internal.pdu_driver import PduDriver


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


log = _Log()

cfg_normal = ET.fromstring("""
                <pdu brand="raritan" model="px-5052R">
                    <ip>10.239.129.19</ip>
                    <port>22</port>
                    <username>admin</username>
                    <password>intel@123</password>
                    <timeout>
                        <invoke>5</invoke>
                    </timeout>
                    <outlets>
                        <outlet>1</outlet>
                        <outlet>2</outlet>
                    </outlets>
                </pdu>
""")


class SshMock():

    def __init__(self, return_value=None, send_cmd=None, *args, **kwargs):
        self.return_value = return_value
        self.send_cmd = send_cmd

    def set_missing_host_key_policy(self, *args, **kwargs):
        return None

    def connect(self, *args, **kwargs):
        return None

    def get_transport(self, *args, **kwargs):
        return OpenSessionMock(self.return_value, self.send_cmd)

    def close(self, *args, **kwargs):
        return None


class OpenSessionMock():

    def __init__(self, return_value=None, send_cmd=None, *args, **kwargs):
        self.return_value = return_value
        self.send_cmd = send_cmd

    def open_session(self, *args, **kwargs):
        return InvoMock(self.return_value, self.send_cmd)


class InvoMock():

    def __init__(self, return_value=None, send_cmd=None, *args, **kwargs):
        self.return_value = return_value
        self.send_cmd = send_cmd

    def get_pty(self, *args, **kwargs):
        return None

    def invoke_shell(self, *args, **kwargs):
        return None

    def sendall(self, *args, **kwargs):
        return None

    def recv(self, *args, **kwargs):
        if self.return_value == "On":
            return b'On'
        elif self.return_value == "Off":
            return b'Off'
        else:
            raise

    def close(self, *args, **kwargs):
        return None

class StateMock(object):
    pass

class TestPduDriver():


    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.pdu_driver.RaritanPowerstate')
    @pytest.mark.parametrize('ret, state', [([(1, "On")], True),
                                             ([(2, "Off")], False)])
    def test_get_ac_power_state(state_mock, ret, state):
        state_mock.return_value = mock.MagicMock()
        state_mock.return_value.wait_result.return_value = ret
        with PduDriver(cfg_opts=cfg_normal, log=log) as pd_obj:
            ret = pd_obj.get_ac_power_state(timeout=10)
            assert ret == state

    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.pdu_driver.RaritanPoweron')
    @mock.patch('dtaf_core.drivers.internal.pdu_driver.PduDriver.get_ac_power_state')
    @pytest.mark.parametrize('ret, state', [(True, True),
                                            (False, False)])
    def test_ac_power_on(state_mock, power_mock, ret, state):
        power_mock.return_value = mock.MagicMock()
        state_mock.return_value = ret
        with PduDriver(cfg_opts=cfg_normal, log=log) as pd_obj:
            r = pd_obj.ac_power_on(10)
            assert r == state


    @staticmethod
    @mock.patch('dtaf_core.drivers.internal.pdu_driver.RaritanPoweroff')
    @mock.patch('dtaf_core.drivers.internal.pdu_driver.PduDriver.get_ac_power_state')
    @pytest.mark.parametrize('ret, state', [(True, False),
                                            (False, True)])
    def test_ac_power_on(state_mock, power_mock, ret, state):
        power_mock.return_value = mock.MagicMock()
        state_mock.return_value = ret
        with PduDriver(cfg_opts=cfg_normal, log=log) as pd_obj:
            r = pd_obj.ac_power_off(10)
            assert r == state
