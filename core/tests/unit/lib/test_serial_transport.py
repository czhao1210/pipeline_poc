import six


if six.PY2:
    import mock

if six.PY3 or six.PY34:
    from unittest import mock

from dtaf_core.lib.private.serial_transport import *


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


class _Serial(object):
    def __init__(self, data):
        self.__count = 0
        self.__data = data
        self.side_effect = tuple()

    def read_from(self, buffer_name):
        if isinstance(self.__data, tuple):
            cur = self.__count
            self.__count += 1
            return self.__data[cur]
        else:
            return self.__data

    def write(self, data):
        if self.side_effect:
            cur = self.__count
            self.__count += 1
            raise self.side_effect[cur]


class TestSerialTransport(object):
    @staticmethod
    def test_misc():
        ret = length_char("aa", 2*len("aa"))
        assert len(ret) == 2*len("aa")
        assert ret.startswith("0"*len("aa"))
        start = datetime.now()
        assert calculate_timeout(start, 10)
        assert calculate_timeout(start, 0)

    @staticmethod
    @mock.patch("dtaf_core.lib.private.shared_data.SerialOutputCapture.get_instance")
    def test_recv(socMock):
        #
        has_exception = False
        socMock.return_value.return_on_detection.return_value = False
        try:
            assert not receive_frame(_Log(), _Serial(chr(0x7E) + chr(0x24)+"10zz123456something"), "test", 5)
        except Exception as ex:
            print(ex)
            has_exception = True
        assert has_exception
        # normal
        has_exception = False
        socMock.return_value.return_on_detection.return_value = False
        try:
            assert not receive_frame(_Log(), _Serial(chr(0x7E) + chr(0x24)+"1035123456something"), "test", 5)
        except TransportTimeout as ex:
            print(ex)
            has_exception = True
        assert has_exception
        # normal
        has_exception = False
        socMock.return_value.return_on_detection.return_value = False
        try:
            assert not receive_frame(_Log(), _Serial(chr(0x7E) + chr(0x24)+"1935123456something"), "test", 5)
        except TransportTimeout as ex:
            print(ex)
            has_exception = True
        assert has_exception
        # raise
        socMock.return_value.return_on_detection.return_value = True
        has_exception = False
        try:
            assert receive_frame(_Log(), _Serial("something"), "test", 5)
        except Exception as ex:
            has_exception = True
        assert has_exception

    @staticmethod
    def test_send():
        ser_mocker = _Serial("")
        send_frame(_Log(), _Serial(""), "test")
        ser_mocker.side_effect = (SerialTimeoutException("UT"), SerialException("UT"))
        has_exception = False
        try:
            send_frame(_Log(), ser_mocker, "test"*16)
        except TransportTimeout as ex:
            has_exception = True
        assert has_exception
        has_exception = False
        try:
            send_frame(_Log(), ser_mocker, "test"*16)
        except TransportError as ex:
            has_exception = True
        assert has_exception

    @staticmethod
    def test_frame():
        has_exception = False
        try:
            frm = Frame("100")
        except ValueError as error:
            has_exceptoin = True
        assert has_exceptoin
        frm = Frame.parse(_Log(), "~$1016"+"b"*16)
        ret = "~$1016"+"b"*16
        assert  frm.get_frame_data(_Log).startswith(ret)

    @staticmethod
    @mock.patch("dtaf_core.lib.private.serial_transport.send_frame", return_value=None)
    @mock.patch("dtaf_core.lib.private.serial_transport.receive_frame")
    @mock.patch("dtaf_core.lib.private.shared_data.SerialOutputCapture.get_instance")
    def test_recv_msg(socMock, recvMock, sendMock):
        #
        recvMock.side_effect = ["~$4016"+"b"*16, "~$3016"+"b"*16]
        has_exception = False
        socMock.return_value.return_on_detection.return_value = False
        Message.receive(_Log(), _Serial(chr(0x7E) + chr(0x24) + "4035123456something"), "test", 30)

    @staticmethod
    @mock.patch("dtaf_core.lib.private.serial_transport.send_frame", return_value=None)
    @mock.patch("dtaf_core.lib.private.serial_transport.receive_frame")
    @mock.patch("dtaf_core.lib.private.shared_data.SerialOutputCapture.get_instance")
    def test_send_msg(socMock, recvMock, sendMock):
        #
        recvMock.side_effect = [
            "~$5016"+"b"*16, "~$5016"+"4",
            "~$5016"+"b"*16, "~$5016"+"4",
            "~$5016"+"b"*16, "~$5016"+"4",
            "~$5016"+"b"*16, "~$5016"+"4",
            "~$5016"+"b"*16, "~$5016"+"4",
        ]
        has_exception = False
        socMock.return_value.return_on_detection.return_value = False
        try:
            Message.send(_Log(), _Serial(chr(0x7E) + chr(0x24) + "4035123456something"), "test","test"*16)
        except Exception as  ex:
            pass

