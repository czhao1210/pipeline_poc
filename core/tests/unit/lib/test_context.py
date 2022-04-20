from dtaf_core.lib.private.context import *
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


class TestContext(object):

    @staticmethod
    def test_get():
        device = mock.Mock()
        obj = ContextInstance(device, logger=_Log())
        obj.get(logger=_Log())

    @staticmethod
    def test_set_output_capture():
        device = mock.Mock()
        obj = ContextInstance(device, logger=_Log())
        obj.set_output_capture([1])

    @staticmethod
    def test_delete():
        device = mock.Mock()
        obj = ContextInstance(device, logger=_Log())
        obj.delete()
