from testcase_template import BaseTestCase
from dtaf_core.lib.test_context import TestContext


class Driver(object):
    """
    Fake Driver Used for demo only
    """
    def __init__(self, seq):
        self.__seq = seq

    def __enter__(self):
        print(r"Driver enter {}".format(self.__seq))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(r"Driver exit {}".format(self.__seq))

    def test_driver(self):
        print(r"test driver {}".format(self.__seq))


class DriverFactory(object):
    """
    Fake Driver Factory Used for demo only
    """
    @staticmethod
    def create(seq):
        d = Driver(seq)
        print(r"Factory enter context begin")
        TestContext().enter_context(d)
        print(r"Factory enter context end")
        return d


class Provider(object):
    """
    Fake Provider Used for demo only
    """
    def __init__(self, seq):
        self.__driver = DriverFactory.create(seq)

    def __enter__(self):
        print(r"Provider enter")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(r"Provider exits")

    def test(self):
        self.__driver.test_driver()


class SampleTest(BaseTestCase):
    def prepare(self):
        print(r"sample test prepare")

    def cleanup(self):
        print(r"sample test cleanup")

    def test_normal(self):
        print(r"test normal in sample test")
        p1 = Provider(1)
        p1.test()
        with Provider(2) as p_with:
            p_with.test()
        p3 = Provider(3)
        p3.test()

    def test_abnormal(self):
        print(r"test abnormal in sample test")
        p1 = Provider(11)
        p1.test()
        with Provider(22) as p_with:
            p_with.test()
        p3 = Provider(33)
        p3.test()


if __name__ == "__main__":
    SampleTest().execute()
