import xml.etree.ElementTree as ET
from dtaf_core.drivers.internal.socket_driver import SocketDriver
import pytest
import mock
import socket


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
                        <socket>
                            <ip>127.0.0.1</ip>
                            <port>5555</port>
                            <bufsize>1030</bufsize>
                        </socket>
""")


class SocketMocketMock:
    def __init__(self, bind_func, ConnMock_recv_value=b"sendtest", recv_func=None, send_func=None,
                 conn_recv_error_number=None, *args,
                 **kwargs):
        self.bind_func = bind_func
        self.ConnMock_recv_value = ConnMock_recv_value
        self.recv_func = recv_func
        self.send_func = send_func
        self.conn_recv_error_number = conn_recv_error_number

    def setsockopt(self, *args, **kwargs):
        return True

    def bind(self, *args, **kwargs):
        return self.bind_func()

    def close(self, *args, **kwargs):
        return True

    def settimeout(self, *args, **kwargs):
        return True

    def listen(self, *args, **kwargs):
        return True

    def accept(self, *args, **kwargs):
        return [ConnMock(recv_value=self.ConnMock_recv_value, recv_func=self.recv_func, send_func=self.send_func,
                         recv_error_number=self.conn_recv_error_number), address_mock()]


class ConnMock:

    def __init__(self, recv_value=None, recv_func=None, send_func=None, recv_error_number=None):
        self.recv_value = recv_value
        self.recv_func = recv_func
        self.send_func = send_func
        self.recv_error_number = recv_error_number

    def settimeout(self, *args, **kwargs):
        return True

    def recv(self, *args, **kwargs):
        if self.recv_func:
            self.recv_func()
        if self.recv_error_number == 'abc':
            self.recv_error_number = 'cba'
            return self.recv_value
        if not self.recv_error_number:
            return self.recv_value
        else:
            raise Exception('My error')

    def close(self, *args, **kwargs):
        return True

    def send(self, *args, **kwargs):
        if self.send_func:
            self.send_func()
        return True


def address_mock():
    return ['127.0.0.1', 'x.x.x.x']


def bind_func():
    return True


def error_func1():
    raise socket.error("My error.")


def error_func2():
    raise socket.timeout("My error.")


class DatetimeDatetimeMock():
    def __init__(self, NowMock_seconds):
        self.NowMock_seconds = NowMock_seconds

    def now(self):
        return NowMock(self.NowMock_seconds)


class NowMock():
    def __init__(self, seconds):
        self.seconds = seconds

    def __sub__(self, other):
        return NowMock(self.seconds)


class PopenMock():
    def __init__(self, *args, **kwargs):
        pass

    def readlines(self, *args, **kwargs):
        return "Reply from"


class TestSocketDriver(object):

    @staticmethod
    @pytest.mark.parametrize("error_type", ['a', 'b'])
    def test_open(error_type):
        from dtaf_core.drivers.internal.socket_driver import socket
        socket.timeout = Exception
        error_func = None
        socket.socket = mock.Mock(return_value=SocketMocketMock(bind_func=error_func))
        try:
            with SocketDriver(cnf_normal, log) as sd_obj:
                pass
        except:
            pass

    # @staticmethod
    # @pytest.mark.parametrize("data,NowMock_seconds,recv_error_number,recv_error_type",
    #                          [(b"sendtest", 30, None, "c"),
    #                           (b"sendtest", 29, None, "c"),
    #                           ])
    # def test_receive(data, NowMock_seconds, recv_error_number, recv_error_type):
    #     from dtaf_core.drivers.internal.socket_driver import socket
    #     from dtaf_core.drivers.internal import socket_driver
    #     socket.timeout = Exception
    #     error_func = None
    #     socket_driver.__dict__['datetime'] = DatetimeDatetimeMock(NowMock_seconds)
    #     socket.socket = mock.Mock(return_value=SocketMocketMock(bind_func=bind_func, ConnMock_recv_value=data,
    #                                                             conn_recv_error_number=recv_error_number,
    #                                                             recv_func=error_func))
    #     with SocketDriver(cnf_normal, log) as sd_obj:
    #         try:
    #             sd_obj.receive(timeout=10)
    #         except:
    #             pass

    @staticmethod
    @pytest.mark.parametrize("send_data,send_error_type", [("a" * 1031, "c"),
                                                           ])
    def test_send(send_data, send_error_type):
        from dtaf_core.drivers.internal.socket_driver import socket
        socket.timeout = Exception
        error_func = None
        socket.socket = mock.Mock(return_value=SocketMocketMock(bind_func=bind_func, send_func=error_func))
        with SocketDriver(cnf_normal, log) as sd_obj:
            try:
                sd_obj.send(data=send_data)
            except:
                pass
