from dtaf_core.lib.private.cl_utils.communication.session import Session
import mock


class TestSuites:
    @mock.patch('dtaf_core.lib.private.cl_utils.communication.session.ExecutionService')
    def test_get_property(self, ReceiveService_mock):
        obj = Session('xxx//:xxxx//:xxx')
        a = obj.context
        b = obj.bind_port
        c = obj.bind_address
        d = obj.dest_address
        f = obj.src_address

    @mock.patch('dtaf_core.lib.private.cl_utils.communication.session.ExecutionService')
    def test_execute_async(self, ReceiveService_mock):
        obj = Session('xxx//:xxxx//:xxx')
        obj.execute_async('a', 'b')

    