from dtaf_core.lib.private.cl_utils.communication.local.general import remote_execute
import mock


class TestSuites(object):

    @staticmethod
    @mock.patch('dtaf_core.lib.private.cl_utils.communication.local.general.Session')
    def test_init(session_mock):
        session_mock.return_value = mock.Mock()
        session_mock.return_value.execute_async.return_value={'key':123}
        remote_execute('a//:b//:c//:d', 'b', 'c')
