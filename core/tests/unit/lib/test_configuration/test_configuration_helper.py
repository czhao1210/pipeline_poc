from unittest import TestCase
from unittest import main as ut_main

class ConfigurationHelperUnitTest(TestCase):
    def setUp(self):
        super(ConfigurationHelperUnitTest, self).setUp()

    def tearDown(self):
        super(ConfigurationHelperUnitTest, self).tearDown()

    def testNormal(self):
        print("test")
        self.assertTrue(True, "Test")


if __name__ == r"__main__":
    ut_main()