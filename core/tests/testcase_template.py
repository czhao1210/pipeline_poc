from dtaf_core.lib.test_context import TestContext


class BaseTestCase(object):
    def prepare(self):
        pass

    def cleanup(self):
        pass

    def execute(self):
        with TestContext():
            func_list = list(filter(
                lambda m: m.startswith("test") and callable(getattr(self, m)),
                dir(self)))
            for func_name in func_list:
                func = getattr(self, func_name)
                self.prepare()
                func()
                self.cleanup()
