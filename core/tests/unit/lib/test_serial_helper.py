from dtaf_core.lib.private.serial_helper import *
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


class AMock():
    def __init__(self, *args, **kwargs):
        return


class TestSerialHelper(object):

    @staticmethod
    def test_set_filter_data():
        obj = FilterSerial()
        obj.set_filter_data(list())

    @staticmethod
    def test_clear_filter_data():
        obj = FilterSerial()
        obj.clear_filter_data()

    @staticmethod
    def test_get():
        obj = FilterSerial()
        obj.get()

    @staticmethod
    def test_read_frame():
        AMock = mock.Mock()
        AMock.read_from.return_value = 'abc'
        obj = SerialHelper(AMock, _Log(), 1)
        obj.read_frame(1, 'a', 1)

    @staticmethod
    def test_read_until():
        AMock = mock.Mock()
        AMock.read_from.return_value = 'abc'
        obj = SerialHelper(AMock, _Log(), 1)
        obj.read_until('a', 1)

    @staticmethod
    def test_read():
        AMock = mock.Mock()
        AMock.read_from.return_value = 'abc'
        obj = SerialHelper(AMock, _Log(), 1)
        obj.read()

    @staticmethod
    def test_write():
        AMock = mock.Mock()
        AMock.read_from.return_value = 'abc'
        obj = SerialHelper(AMock, _Log(), 1)
        obj.write('a')

    @staticmethod
    def test_clean_buffer():
        AMock = mock.Mock()
        AMock.read_from.return_value = 'abc'
        obj = SerialHelper(AMock, _Log(), 1)
        obj.clean_buffer()
