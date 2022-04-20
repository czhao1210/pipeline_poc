from dtaf_core.lib.private.cl_utils.communication.private.executor import *
import mock


class task_mock():
    def __init__(self, *args, **kwargs):
        return

    def daemon(self, *args, **kwargs):
        return True

    def start(self, *args, **kwargs):
        return True


class TestSuites(object):
    @staticmethod
    def test_set():
        obj = ReceiveService()
        obj.set('a')

    @staticmethod
    def test_get():
        obj = ReceiveService()
        obj.get()

    @staticmethod
    def test_executionService():
        from dtaf_core.lib.private.cl_utils.communication.private.executor import Thread, zmq
        Thread.__init__ = task_mock.__init__
        zmq.Context = mock.Mock()
        try:
            obj = ExecutionService('a', 'b')
        except RuntimeError:
            return

    @staticmethod
    def test_executionService2():
        from dtaf_core.lib.private.cl_utils.communication.private.executor import Thread, zmq
        Thread.__init__ = task_mock.__init__
        Thread.daemon = task_mock.daemon
        Thread.start = task_mock.start
        zmq.Context = mock.Mock()
        obj = ExecutionService('a', 'b')
        obj.get('a', 'b')
        print(obj.bind_port, obj.bind_address, obj.address)
        obj.get_message('a')
        obj.stop()
        obj.run()
