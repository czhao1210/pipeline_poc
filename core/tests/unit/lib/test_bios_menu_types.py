from dtaf_core.lib.private.globals.bios_menu_types import *

class TestSuites(object):

    @staticmethod
    def test_types():
        for k in globals():
            print(globals()[k])
