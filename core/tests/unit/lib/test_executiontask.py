from dtaf_core.lib.private.cl_utils.communication.private.executiontask import ExecutionReturnTask, ExecutionTask
import mock


class task_mock():
    def __init__(self, *args, **kwargs):
        return


class TestSuites(object):

    @staticmethod
    def test_ExecutionReturnTask():
        from dtaf_core.lib.private.cl_utils.communication.private.executiontask import Task
        Task.__init__ = task_mock.__init__
        obj = ExecutionReturnTask(1, 2, 3, 4, 5, mock.Mock())
        obj.run()

    @staticmethod
    def test_ExecutionTask():
        from dtaf_core.lib.private.cl_utils.communication.private.executiontask import Task
        Task.__init__ = task_mock.__init__
        obj = ExecutionTask(1, 2, 3, 4, 5, 6)
        obj.run()
