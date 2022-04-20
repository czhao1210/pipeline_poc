from dtaf_core.lib.base_system_test import BaseSystemTest
import mock


class TestSuites:
    @mock.patch('dtaf_core.lib.base_system_test.ExitStack')
    def test_set(self, ExitStack_mock):
        obj = BaseSystemTest()
        obj.class_config = mock.Mock()
        obj.CLASS_UNDER_TEST = mock.Mock()
        obj.addCleanup = mock.Mock()
        obj.setUp()
