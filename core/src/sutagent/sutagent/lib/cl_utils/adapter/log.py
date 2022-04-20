import sys


class sparklogger():
    @staticmethod
    def debug(data):
        f_name = sys._getframe().f_back.f_code.co_name
        f_line = sys._getframe().f_back.f_lineno

        print('{0} {1} DEBUG: {2}'.format(f_name, f_line, data))

    @staticmethod
    def info(data):
        f_name = sys._getframe().f_back.f_code.co_name
        f_line = sys._getframe().f_back.f_lineno

        print('{0} {1} DEBUG: {2}'.format(f_name, f_line, data))

    @staticmethod
    def error(data):
        f_name = sys._getframe().f_back.f_code.co_name
        f_line = sys._getframe().f_back.f_lineno

        print('{0} {1} DEBUG: {2}'.format(f_name, f_line, data))
