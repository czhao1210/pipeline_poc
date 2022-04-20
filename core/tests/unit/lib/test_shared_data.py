from dtaf_core.lib.private.shared_data import *


def mocker(*args, **kwargs):
    return


class TestSuites:

    @staticmethod
    def test_performance():
        performance(mocker)()

    @staticmethod
    def test_get_instance():
        obj = SerialOutputCapture()
        obj.get_instance()

    @staticmethod
    def test_feed():
        obj = SerialOutputCapture()
        obj.feed(mocker)

    @staticmethod
    def test_set_capture_pattern_list():
        obj = SerialOutputCapture()
        obj.set_capture_pattern_list(mocker)

    @staticmethod
    def test_clean():
        obj = SerialOutputCapture()
        obj.clean()

    @staticmethod
    def test_return_on_detection():
        obj = SerialOutputCapture()
        obj.return_on_detection()

    @staticmethod
    def test_get_result():
        obj = SerialOutputCapture()
        obj.get_result()
